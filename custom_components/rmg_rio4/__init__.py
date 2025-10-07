"""
Intégration Home Assistant pour boîtier relais TCP
Connexion via TCP sur port 22023
"""
import asyncio
import logging
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import Platform

_LOGGER = logging.getLogger(__name__)

DOMAIN = "rmg_rio4"
PLATFORMS = [Platform.SWITCH]


class RelayBoxConnection:
    """Gestion de la connexion TCP avec le boîtier relais"""
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.callbacks = []
        
    async def connect(self):
        """Établit la connexion TCP et authentifie"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            _LOGGER.info(f"Connecté à {self.host}:{self.port}")
            
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
                        _LOGGER.info("Authentification réussie")
                        
                        # Démarrer l'écoute des messages
                        asyncio.create_task(self._listen())
                        return True
                    else:
                        _LOGGER.error(f"Échec de l'authentification: {auth_message}")
                        return False
                else:
                    _LOGGER.error(f"Réponse inattendue du serveur: {message}")
                    return False
                    
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout en attendant LOGINREQUEST")
                return False
                    
        except Exception as e:
            _LOGGER.error(f"Erreur de connexion: {e}")
            return False
    
    async def _listen(self):
        """Écoute en continu les messages du serveur"""
        buffer = ""
        while self.connected:
            try:
                data = await self.reader.read(1024)
                if not data:
                    _LOGGER.warning("Connexion fermée par le serveur")
                    self.connected = False
                    # Tentative de reconnexion après 5 secondes
                    await asyncio.sleep(5)
                    await self._reconnect()
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
                        
            except Exception as e:
                _LOGGER.error(f"Erreur lors de l'écoute: {e}")
                self.connected = False
                # Tentative de reconnexion après 5 secondes
                await asyncio.sleep(5)
                await self._reconnect()
                break
    
    async def _reconnect(self):
        """Tente une reconnexion automatique"""
        _LOGGER.info("Tentative de reconnexion...")
        try:
            if await self.connect():
                _LOGGER.info("Reconnexion réussie")
            else:
                _LOGGER.error("Échec de la reconnexion")
        except Exception as e:
            _LOGGER.error(f"Erreur de reconnexion: {e}")
    
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
    
    async def send_command(self, command: str):
        """Envoie une commande au boîtier"""
        if not self.connected:
            _LOGGER.error("Non connecté au boîtier")
            return False
        
        try:
            # Ajouter \r à la fin de la commande
            self.writer.write(f"{command}\r".encode('utf-8'))
            await self.writer.drain()
            _LOGGER.debug(f"Commande envoyée: {command}")
            return True
        except Exception as e:
            _LOGGER.error(f"Erreur lors de l'envoi: {e}")
            return False
    
    async def disconnect(self):
        """Ferme la connexion"""
        self.connected = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()


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
    
    # Enregistrer le service PULSE
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
        await connection.send_command(command)
        _LOGGER.info(f"Commande PULSE envoyée: {command}")
    
    hass.services.async_register(DOMAIN, "pulse_relay", handle_pulse_relay)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Déchargement de l'intégration"""
    connection = hass.data[DOMAIN][entry.entry_id]
    await connection.disconnect()
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok