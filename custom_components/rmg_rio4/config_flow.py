"""
Config flow pour l'intégration du boîtier relais
"""
import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Schéma de configuration
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=22023): int,
    vol.Required(CONF_USERNAME, default="admin"): str,
    vol.Required(CONF_PASSWORD): str,
})


async def validate_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Valide que nous pouvons nous connecter au boîtier"""
    
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    username = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]
    
    try:
        # Tenter une connexion de test
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=10.0
        )
        
        # Attendre le LOGINREQUEST du serveur
        login_request = await asyncio.wait_for(reader.read(100), timeout=5.0)
        message = login_request.decode('utf-8').strip()
        
        if "LOGINREQUEST?" not in message:
            raise Exception("Réponse inattendue du serveur")
        
        # Envoyer les identifiants
        login_string = f"{username};{password}\r"
        writer.write(login_string.encode('utf-8'))
        await writer.drain()
        
        # Vérifier l'authentification
        response = await asyncio.wait_for(reader.read(100), timeout=5.0)
        auth_message = response.decode('utf-8').strip()
        
        # Fermer la connexion de test
        writer.close()
        await writer.wait_closed()
        
        if "AUTHENTICATION=Successful" not in auth_message:
            raise Exception("Authentification échouée")
        
        return {"title": f"RMG Rio 4 ({host})"}
        
    except asyncio.TimeoutError:
        raise Exception("Timeout lors de la connexion")
    except Exception as e:
        _LOGGER.error(f"Erreur de validation: {e}")
        raise


class RelayBoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration"""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gère l'étape de configuration par l'utilisateur"""
        
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_connection(self.hass, user_input)
                
                # Créer l'entrée de configuration
                return self.async_create_entry(title=info["title"], data=user_input)
                
            except asyncio.TimeoutError:
                errors["base"] = "timeout"
            except Exception as e:
                _LOGGER.exception("Erreur de configuration")
                if "Authentification" in str(e):
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "cannot_connect"
        
        # Afficher le formulaire
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )