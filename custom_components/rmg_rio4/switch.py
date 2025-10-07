"""
Plateforme Switch pour l'intégration RMG Rio 4
"""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure les entités switch depuis une entrée de configuration"""
    
    # Récupérer la connexion depuis le domain
    connection = hass.data[DOMAIN][entry.entry_id]
    
    # Créer les entités switch pour chaque relais (toujours 4 sur un Rio 4)
    entities = []
    for i in range(1, 5):  # Rio 4 = 4 relais
        entities.append(RMGRelay(connection, i))
    
    # Créer les entités DIO (entrées/sorties digitales)
    # Note: Les DI (Digital Input) seront en lecture seule
    # Les DO (Digital Output) pourront être contrôlées
    for i in range(1, 5):  # 4 DIO sur le Rio 4
        entities.append(RMGDIO(connection, i))
    
    async_add_entities(entities, True)


class RMGRelay(SwitchEntity):
    """Représente un relais RMG Rio 4"""
    
    def __init__(self, connection, relay_number: int):
        """Initialise le relais"""
        self._connection = connection
        self._relay_number = relay_number
        self._relay_name = f"RELAY{relay_number}"
        self._is_on = False
        self._available = True
        
        # Attributs Home Assistant
        self._attr_name = f"Relais {relay_number}"
        self._attr_unique_id = f"rmg_rio4_relay_{relay_number}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, connection.host)},
            "name": "RMG Rio 4",
            "manufacturer": "RMG",
            "model": "Rio 4",
            "sw_version": "1.0",
        }
        
        # Enregistrer le callback pour les mises à jour
        connection.register_callback(self._update_callback)
    
    async def _update_callback(self, device: str, state: str):
        """Callback appelé quand un état change"""
        if device == self._relay_name:
            old_state = self._is_on
            self._is_on = (state == "ON")
            if old_state != self._is_on:
                self.async_write_ha_state()
                _LOGGER.debug(f"{self._relay_name} état changé: {state}")
    
    @property
    def is_on(self) -> bool:
        """Retourne si le relais est activé"""
        return self._is_on
    
    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible"""
        return self._available and self._connection.connected
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Active le relais"""
        command = f"{self._relay_name} ON"
        success = await self._connection.send_command(command)
        if success:
            _LOGGER.debug(f"Commande ON envoyée pour {self._relay_name}")
        else:
            _LOGGER.error(f"Échec de la commande ON pour {self._relay_name}")
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Désactive le relais"""
        command = f"{self._relay_name} OFF"
        success = await self._connection.send_command(command)
        if success:
            _LOGGER.debug(f"Commande OFF envoyée pour {self._relay_name}")
        else:
            _LOGGER.error(f"Échec de la commande OFF pour {self._relay_name}")
    
    async def async_pulse(self, duration: float = 0.5) -> None:
        """Active le relais en mode PULSE"""
        command = f"{self._relay_name} PULSE {duration}"
        success = await self._connection.send_command(command)
        if success:
            _LOGGER.debug(f"Commande PULSE {duration}s envoyée pour {self._relay_name}")
        else:
            _LOGGER.error(f"Échec de la commande PULSE pour {self._relay_name}")


class RMGDIO(SwitchEntity):
    """Représente une entrée/sortie digitale RMG Rio 4"""
    
    def __init__(self, connection, dio_number: int):
        """Initialise la DIO"""
        self._connection = connection
        self._dio_number = dio_number
        self._dio_name = f"DIO{dio_number}"
        self._is_on = False
        self._available = True
        self._is_read_only = False  # Sera déterminé dynamiquement
        
        # Attributs Home Assistant
        self._attr_name = f"DIO {dio_number}"
        self._attr_unique_id = f"rmg_rio4_dio_{dio_number}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, connection.host)},
            "name": "RMG Rio 4",
            "manufacturer": "RMG",
            "model": "Rio 4",
            "sw_version": "1.0",
        }
        
        # Enregistrer le callback pour les mises à jour
        connection.register_callback(self._update_callback)
    
    async def _update_callback(self, device: str, state: str):
        """Callback appelé quand un état change"""
        if device == self._dio_name:
            # Détecter si c'est une erreur de type DI
            if "TYPE DI ERROR" in state:
                self._is_read_only = True
                self._attr_name = f"DIO {self._dio_number} (Entrée)"
                _LOGGER.info(f"{self._dio_name} détecté comme entrée digitale (lecture seule)")
                self.async_write_ha_state()
                return
            
            old_state = self._is_on
            self._is_on = (state == "ON")
            if old_state != self._is_on:
                self.async_write_ha_state()
                _LOGGER.debug(f"{self._dio_name} état changé: {state}")
    
    @property
    def is_on(self) -> bool:
        """Retourne si la DIO est activée"""
        return self._is_on
    
    @property
    def available(self) -> bool:
        """Retourne si l'entité est disponible"""
        return self._available and self._connection.connected
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Active la DIO (si c'est une sortie)"""
        # Vérifier si c'est une entrée en mode lecture seule
        if self._is_read_only:
            _LOGGER.warning(f"{self._dio_name} est une entrée digitale (lecture seule)")
            return
        
        command = f"{self._dio_name} ON"
        success = await self._connection.send_command(command)
        if success:
            _LOGGER.debug(f"Commande ON envoyée pour {self._dio_name}")
        else:
            _LOGGER.error(f"Échec de la commande ON pour {self._dio_name}")
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Désactive la DIO (si c'est une sortie)"""
        # Vérifier si c'est une entrée en mode lecture seule
        if self._is_read_only:
            _LOGGER.warning(f"{self._dio_name} est une entrée digitale (lecture seule)")
            return
        
        command = f"{self._dio_name} OFF"
        success = await self._connection.send_command(command)
        if success:
            _LOGGER.debug(f"Commande OFF envoyée pour {self._dio_name}")
        else:
            _LOGGER.error(f"Échec de la commande OFF pour {self._dio_name}")
    
    @property
    def extra_state_attributes(self):
        """Retourne des attributs supplémentaires"""
        attrs = {
            "dio_number": self._dio_number,
            "connection_host": self._connection.host,
        }
        if self._is_read_only:
            attrs["type"] = "Digital Input (lecture seule)"
        else:
            attrs["type"] = "Digital Output (contrôlable)"
        return attrs