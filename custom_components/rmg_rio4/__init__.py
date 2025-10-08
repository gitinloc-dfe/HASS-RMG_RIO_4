"""
Intégration Home Assistant pour boîtier relais TCP RMG Rio 4
Connexion via TCP sur port 22023 avec reconnexion automatique
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import Platform

_LOGGER = logging.getLogger(__name__)

DOMAIN = "rmg_rio4"
PLATFORMS = [Platform.SWITCH]


class RelayBoxConnection:
    """Gestion de la connexion TCP avec le boîtier relais RMG Rio 4
    
    Fonctionnalités:
    - Connexion TCP avec authentification
    - Reconnexion automatique avec backoff exponentiel
    - Surveillance de santé de connexion (ping)
    - Gestion d'état des entités (disponible/indisponible)
    """
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.callbacks: List[Callable] = []
        
        # Paramètres de reconnexion
        self._reconnect_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._reconnect_interval = 5  # Commence à 5 secondes
        self._max_reconnect_interval = 300  # Maximum 5 minutes
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 999  # Tentatives quasi-illimitées
        self._last_successful_connection: Optional[datetime] = None
        self._connection_stable_time = 30  # Connexion stable après 30s
        self._ping_interval = 30  # Ping toutes les 30 secondes
        
        # Entités enregistrées pour notification d'état
        self.entities: List = []
        
    async def connect(self):
        """Établit la connexion TCP et authentifie avec gestion robuste d'erreurs"""
        try:
            _LOGGER.info(f"🔌 Connexion à {self.host}:{self.port}...")
            
            # Nettoyer les anciennes connexions
            await self._cleanup_connection()
            
            # Établir la connexion TCP
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=10.0
            )
            _LOGGER.debug(f"Socket TCP établi vers {self.host}:{self.port}")
            
            # Attendre le LOGINREQUEST du serveur
            try:
                data = await asyncio.wait_for(self.reader.read(100), timeout=5.0)
                message = data.decode('utf-8').strip()
                _LOGGER.debug(f"Reçu: {message}")
                
                if "LOGINREQUEST?" in message:
                    # Envoyer les identifiants
                    login_string = f"{self.username};{self.password}\r"
                    self.writer.write(login_string.encode('utf-8'))
                    await self.writer.drain()
                    _LOGGER.debug(f"Identifiants envoyés: {self.username};***")
                    
                    # Attendre la réponse d'authentification
                    response = await asyncio.wait_for(self.reader.read(100), timeout=5.0)
                    auth_message = response.decode('utf-8').strip()
                    _LOGGER.debug(f"Authentification: {auth_message}")
                    
                    if "AUTHENTICATION=Successful" in auth_message:
                        self.connected = True
                        self._last_successful_connection = datetime.now()
                        _LOGGER.info("✅ Authentification réussie au RMG Rio 4")
                        
                        # Reset des paramètres de reconnexion
                        self._reconnect_attempts = 0
                        self._reconnect_interval = 5
                        
                        # Démarrer l'écoute des messages et la surveillance
                        asyncio.create_task(self._listen())
                        await self._mark_entities_available()
                        
                        return True
                    else:
                        _LOGGER.error(f"❌ Échec de l'authentification: {auth_message}")
                        await self._cleanup_connection()
                        return False
                else:
                    _LOGGER.error(f"Réponse inattendue du serveur: {message}")
                    await self._cleanup_connection()
                    return False
                    
            except asyncio.TimeoutError:
                _LOGGER.error("⏰ Timeout en attendant LOGINREQUEST")
                await self._cleanup_connection()
                return False
                    
        except asyncio.TimeoutError:
            _LOGGER.error(f"⏰ Timeout de connexion vers {self.host}:{self.port}")
            await self._cleanup_connection()
            return False
        except Exception as e:
            _LOGGER.error(f"❌ Erreur de connexion: {e}")
            await self._cleanup_connection()
            return False
    
    async def _cleanup_connection(self):
        """Nettoie la connexion actuelle"""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass  # Ignorer les erreurs de nettoyage
        
        self.reader = None
        self.writer = None
        self.connected = False
    
    async def _listen(self):
        """Écoute en continu les messages du serveur avec gestion robuste des erreurs"""
        buffer = ""
        _LOGGER.debug("👂 Démarrage écoute des messages serveur")
        
        # Démarrer la surveillance de connexion
        await self._start_connection_monitoring()
        
        try:
            while self.connected and self.reader:
                try:
                    data = await asyncio.wait_for(self.reader.read(1024), timeout=60.0)
                    
                    if not data:
                        _LOGGER.warning("📡 Connexion fermée par le serveur")
                        self.connected = False
                        break
                    
                    buffer += data.decode('utf-8')
                    
                    # Traiter les lignes complètes (séparées par \r ou \n)
                    while '\r' in buffer or '\n' in buffer:
                        if '\r' in buffer:
                            line, buffer = buffer.split('\r', 1)
                        else:
                            line, buffer = buffer.split('\n', 1)
                        
                        line = line.strip()
                        if line:
                            await self._process_message(line)
                
                except asyncio.TimeoutError:
                    # Timeout normal - on continue d'écouter
                    _LOGGER.debug("⏰ Timeout écoute (normal)")
                    continue
                    
                except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                    _LOGGER.warning(f"📡 Connexion interrompue: {e}")
                    self.connected = False
                    break
                    
        except asyncio.CancelledError:
            _LOGGER.debug("🛑 Écoute des messages annulée")
        except Exception as e:
            _LOGGER.error(f"❌ Erreur lors de l'écoute: {e}")
            self.connected = False
        finally:
            # Arrêter la surveillance
            if self._monitor_task and not self._monitor_task.done():
                self._monitor_task.cancel()
            
            # Si la connexion a été fermée de façon inattendue, déclencher une reconnexion
            if not self.connected:
                _LOGGER.warning("🔌 Écoute terminée - déclenchement reconnexion")
                asyncio.create_task(self._trigger_reconnect())
    
    async def _ensure_connection(self):
        """Assure que la connexion est active, sinon tente de reconnecter"""
        if not self.connected or not self.writer or self.writer.is_closing():
            _LOGGER.warning("🔌 Connexion fermée, tentative de reconnexion...")
            await self._trigger_reconnect()
            return self.connected
        return True
    
    async def _trigger_reconnect(self):
        """Déclenche une reconnexion si pas déjà en cours"""
        if self._reconnect_task and not self._reconnect_task.done():
            return  # Une reconnexion est déjà en cours
            
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    async def _reconnect_loop(self):
        """Boucle de reconnexion avec stratégie de backoff exponentiel"""
        await self._mark_entities_unavailable()
        
        while self._reconnect_attempts < self._max_reconnect_attempts:
            try:
                self._reconnect_attempts += 1
                _LOGGER.info(f"🔄 Tentative de reconnexion #{self._reconnect_attempts}...")
                
                # Nettoyer l'ancienne connexion
                await self._cleanup_connection()
                
                # Nouvelle tentative de connexion
                success = await self.connect()
                
                if success:
                    _LOGGER.info("✅ Reconnexion réussie au RMG Rio 4")
                    
                    # Démarrer la surveillance de connexion
                    await self._start_connection_monitoring()
                    
                    # Demander les états initiaux après reconnexion
                    await asyncio.sleep(1)
                    await self.request_initial_states(4, 4)
                    
                    return True
                else:
                    raise Exception("Échec de connexion")
                    
            except Exception as e:
                # Calculer le délai avec backoff exponentiel
                delay = min(
                    self._reconnect_interval * (2 ** min(self._reconnect_attempts - 1, 6)), 
                    self._max_reconnect_interval
                )
                
                _LOGGER.warning(f"❌ Reconnexion #{self._reconnect_attempts} échouée: {e}")
                _LOGGER.info(f"⏰ Prochaine tentative dans {delay}s")
                
                # Attendre avant la prochaine tentative
                await asyncio.sleep(delay)
        
        _LOGGER.error(f"❌ Abandon après {self._max_reconnect_attempts} tentatives")
        return False
    
    async def _start_connection_monitoring(self):
        """Démarre la surveillance de santé de connexion"""
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
        
        self._monitor_task = asyncio.create_task(self._monitor_connection_health())
    
    async def _monitor_connection_health(self):
        """Surveille la santé de la connexion en arrière-plan"""
        _LOGGER.debug("🩺 Surveillance de connexion démarrée")
        
        while self.connected:
            try:
                await asyncio.sleep(self._ping_interval)
                
                if not await self._ping_device():
                    _LOGGER.warning("💔 Ping échoué, connexion peut-être fermée")
                    self.connected = False
                    break
                else:
                    _LOGGER.debug("💓 Ping réussi - connexion stable")
                    
            except asyncio.CancelledError:
                _LOGGER.debug("🛑 Surveillance de connexion annulée")
                break
            except Exception as e:
                _LOGGER.error(f"Erreur surveillance connexion: {e}")
                self.connected = False
                break
        
        # La connexion est fermée, déclencher une reconnexion
        if not self.connected:
            _LOGGER.warning("🚨 Connexion fermée détectée par surveillance")
            await self._trigger_reconnect()
    
    async def _ping_device(self):
        """Test de ping pour vérifier que l'appareil répond"""
        try:
            if not self.writer or self.writer.is_closing():
                return False
                
            # Envoyer une commande simple pour tester
            start_time = datetime.now()
            success = await self.send_command("RELAY1?", skip_connection_check=True)
            
            if not success:
                return False
            
            # Le ping est considéré réussi si la commande s'envoie sans erreur
            # La réponse sera traitée normalement par _listen()
            return True
                
        except Exception as e:
            _LOGGER.debug(f"Erreur ping: {e}")
            return False
    
    async def _process_message(self, message: str):
        """Traite les messages reçus du boîtier"""
        _LOGGER.debug(f"Message reçu: {message}")
        
        # Ignorer certains messages de statut
        if message in ["SERVER=SHUTDOWN", "UPDATE=STARTED", "REBOOT=STARTED"]:
            _LOGGER.info(f"Message de statut serveur: {message}")
            return
        
        # Parser les états des relais et DIOs (RELAY1=OFF, DIO1=OFF, etc.)
        if "=" in message and (message.startswith("RELAY") or message.startswith("DIO")):
            try:
                device, state = message.split("=", 1)
                device = device.strip()
                state = state.strip()
                
                # Vérifier que l'état est valide ou si c'est une erreur de type
                if state in ["ON", "OFF"] or "ERROR" in state:
                    # Notifier tous les callbacks enregistrés
                    for callback in self.callbacks:
                        try:
                            await callback(device, state)
                        except Exception as e:
                            _LOGGER.error(f"Erreur dans callback pour {device}={state}: {e}")
                else:
                    _LOGGER.warning(f"État invalide reçu: {message}")
            except Exception as e:
                _LOGGER.error(f"Erreur parsing message {message}: {e}")
        elif "ERROR=" in message:
            _LOGGER.error(f"Erreur du serveur: {message}")
        else:
            _LOGGER.debug(f"Message non traité: {message}")
    
    def register_callback(self, callback):
        """Enregistre un callback pour les mises à jour d'état"""
        self.callbacks.append(callback)
    
    def register_entity(self, entity):
        """Enregistre une entité pour la gestion d'état disponible/indisponible"""
        if entity not in self.entities:
            self.entities.append(entity)
    
    async def _mark_entities_available(self):
        """Marque toutes les entités comme disponibles"""
        for entity in self.entities:
            if hasattr(entity, 'set_available'):
                entity.set_available(True)
                if hasattr(entity, 'async_write_ha_state'):
                    entity.async_write_ha_state()
    
    async def _mark_entities_unavailable(self):
        """Marque toutes les entités comme indisponibles"""
        for entity in self.entities:
            if hasattr(entity, 'set_available'):
                entity.set_available(False)
                if hasattr(entity, 'async_write_ha_state'):
                    entity.async_write_ha_state()
    
    async def request_initial_states(self, num_relays=4, num_dios=4):
        """Demande les états initiaux de tous les relais et DIOs"""
        if not self.connected:
            return
        
        try:
            # Demander l'état de chaque relais
            for i in range(1, num_relays + 1):
                await self.send_command(f"RELAY{i}?")
                await asyncio.sleep(0.1)  # Petit délai pour éviter le spam
            
            # Demander l'état de chaque DIO
            for i in range(1, num_dios + 1):
                await self.send_command(f"DIO{i}?")
                await asyncio.sleep(0.1)
                
            _LOGGER.debug("États initiaux demandés")
        except Exception as e:
            _LOGGER.error(f"Erreur lors de la demande des états initiaux: {e}")
    
    async def send_command(self, command: str, skip_connection_check: bool = False):
        """Envoie une commande avec gestion automatique de reconnexion"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Vérifier/assurer la connexion sauf si explicitement ignoré
                if not skip_connection_check:
                    if not await self._ensure_connection():
                        if attempt < max_retries - 1:
                            await asyncio.sleep(0.5)
                            continue
                        _LOGGER.error("❌ Impossible d'établir la connexion pour envoyer la commande")
                        return False
                
                # Vérifier que la connexion est toujours valide
                if not self.writer or self.writer.is_closing():
                    raise ConnectionError("Writer fermé")
                
                # Envoyer la commande
                command_with_cr = f"{command}\r"
                self.writer.write(command_with_cr.encode('utf-8'))
                await self.writer.drain()
                _LOGGER.debug(f"📤 Commande envoyée: {command}")
                return True
                
            except (ConnectionError, OSError, BrokenPipeError, AttributeError) as e:
                _LOGGER.warning(f"⚠️ Erreur envoi commande (tentative {attempt + 1}): {e}")
                
                # Marquer la connexion comme fermée
                self.connected = False
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5)
                    continue
                else:
                    # Déclencher une reconnexion en arrière-plan pour les prochaines commandes
                    asyncio.create_task(self._trigger_reconnect())
                    return False
        
        return False
    
    async def disconnect(self):
        """Ferme proprement la connexion et annule toutes les tâches"""
        _LOGGER.info("🔌 Fermeture connexion RMG Rio 4")
        
        # Marquer comme déconnecté
        self.connected = False
        
        # Annuler les tâches de surveillance et reconnexion
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
        
        # Fermer la connexion TCP
        await self._cleanup_connection()
        
        # Marquer toutes les entités comme indisponibles
        await self._mark_entities_unavailable()
        
        _LOGGER.info("✅ Connexion fermée proprement")
    
    def force_reconnect(self):
        """Force une reconnexion immédiate (pour service de reconnexion manuelle)"""
        _LOGGER.info("🔄 Reconnexion forcée demandée")
        self.connected = False
        self._reconnect_attempts = 0  # Reset le compteur
        asyncio.create_task(self._trigger_reconnect())


class RelaySwitch(SwitchEntity):
    """Représente un relais comme un switch Home Assistant"""
    
    def __init__(self, connection: RelayBoxConnection, relay_name: str, relay_number: int):
        self._connection = connection
        self._relay_name = relay_name
        self._relay_number = relay_number
        self._is_on = False
        self._attr_name = f"Relais {relay_number}"
        self._attr_unique_id = f"relay_box_{relay_name}"
        
        # Enregistrer le callback pour les mises à jour
        connection.register_callback(self._update_callback)
    
    async def _update_callback(self, device: str, state: str):
        """Callback appelé quand un état change"""
        if device == self._relay_name:
            self._is_on = (state == "ON")
            self.async_write_ha_state()
    
    @property
    def is_on(self):
        """Retourne l'état actuel du relais"""
        return self._is_on
    
    async def async_turn_on(self, **kwargs):
        """Active le relais"""
        command = f"{self._relay_name} ON"
        await self._connection.send_command(command)
    
    async def async_turn_off(self, **kwargs):
        """Désactive le relais"""
        command = f"{self._relay_name} OFF"
        await self._connection.send_command(command)
    
    async def async_pulse(self, duration: float = 0.5):
        """Active le relais en mode PULSE (impulsion temporaire)"""
        command = f"{self._relay_name} PULSE {duration}"
        await self._connection.send_command(command)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configuration de l'intégration"""
    host = entry.data["host"]
    port = entry.data.get("port", 22023)
    username = entry.data["username"]
    password = entry.data["password"]
    
    # Créer la connexion
    connection = RelayBoxConnection(host, port, username, password)
    
    # Se connecter
    if not await connection.connect():
        _LOGGER.error("Impossible de se connecter au boîtier")
        return False
    
    # Stocker la connexion
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = connection
    
    # Demander les états initiaux (le serveur envoie automatiquement les états à la connexion)
    # Mais on peut en demander d'autres si besoin
    await asyncio.sleep(1)  # Laisser le temps de recevoir les états automatiques
    await connection.request_initial_states(4, 4)  # Rio 4 = toujours 4 relais et 4 DIO
    
    # Charger les plateformes (switch, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Services de l'intégration
    async def handle_pulse_relay(call):
        """Gère l'appel du service pulse_relay"""
        entity_id = call.data.get("entity_id")
        duration = call.data.get("duration", 0.5)
        
        # Récupérer l'entité
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error(f"Entité {entity_id} non trouvée")
            return
        
        # Extraire le numéro de relais depuis l'entity_id
        # Format attendu: switch.relais_1, switch.relais_2, etc.
        relay_number = entity_id.split("_")[-1]
        relay_name = f"RELAY{relay_number}"
        
        # Envoyer la commande PULSE
        command = f"{relay_name} PULSE {duration}"
        success = await connection.send_command(command)
        if success:
            _LOGGER.info(f"✅ Commande PULSE envoyée: {command}")
        else:
            _LOGGER.error(f"❌ Échec commande PULSE: {command}")
    
    async def handle_reconnect(call):
        """Gère l'appel du service de reconnexion forcée"""
        _LOGGER.info("🔄 Service de reconnexion appelé")
        connection.force_reconnect()
    
    # Enregistrer les services
    hass.services.async_register(DOMAIN, "pulse_relay", handle_pulse_relay)
    hass.services.async_register(DOMAIN, "reconnect", handle_reconnect)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Déchargement de l'intégration"""
    connection = hass.data[DOMAIN][entry.entry_id]
    await connection.disconnect()
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok