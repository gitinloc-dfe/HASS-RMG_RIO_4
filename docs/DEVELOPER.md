# Guide du développeur - RMG Rio 4

## Architecture de l'intégration

L'intégration Home Assistant pour RMG Rio 4 est composée de plusieurs fichiers :

### Structure des fichiers

```
custom_components/rmg_rio4/
├── __init__.py          # Logique principale et gestion TCP
├── config_flow.py       # Interface de configuration
├── switch.py            # Entités relais et DIO
├── services.yaml        # Définition du service PULSE
├── strings.json         # Textes d'interface
├── manifest.json        # Métadonnées du module
└── translations/        # Traductions
    ├── fr.json
    └── en.json
```

## Classes principales

### RelayBoxConnection (`__init__.py`)

Gère la connexion TCP avec le boîtier RMG Rio 4.

**Méthodes importantes :**
- `connect()` : Établit la connexion et authentifie
- `send_command()` : Envoie une commande au boîtier
- `register_callback()` : Enregistre un callback pour les mises à jour
- `_listen()` : Écoute en continu les messages du serveur

**États gérés :**
- `connected` : True si connecté
- `callbacks` : Liste des callbacks pour les mises à jour
- `reader/writer` : Streams TCP

### RMGRelay (`switch.py`)

Représente un relais comme entité switch Home Assistant.

**Méthodes importantes :**
- `async_turn_on()` : Active le relais (`RELAY1 ON`)
- `async_turn_off()` : Désactive le relais (`RELAY1 OFF`)
- `async_pulse()` : Active en mode impulsion (`RELAY1 PULSE durée`)

### RMGDIO (`switch.py`)

Représente une entrée/sortie digitale.

**Caractéristiques :**
- Gère les DI (Digital Input) en lecture seule
- Gère les DO (Digital Output) en écriture
- Détection automatique du type via les réponses d'erreur

## Protocole de communication

### Séquence d'authentification

1. Connexion TCP sur port 22023
2. Serveur envoie : `LOGINREQUEST?\r`
3. Client envoie : `username;password\r`
4. Serveur répond : `AUTHENTICATION=Successful\r` ou `AUTHENTICATION=Failed\r`

### Format des commandes

Toutes les commandes se terminent par `\r` :

```python
# Exemples de commandes
await connection.send_command("RELAY1 ON")      # Active relais 1
await connection.send_command("RELAY2 OFF")     # Désactive relais 2
await connection.send_command("RELAY3 PULSE 2") # Impulsion 2 secondes
await connection.send_command("DIO1?")          # Demande état DIO1
```

### Messages reçus du serveur

Le serveur envoie automatiquement :

1. **États initiaux** à la connexion
2. **Changements d'état** en temps réel
3. **Réponses aux commandes**

Format : `DEVICE=STATE\r`

Exemples :
- `RELAY1=ON\r`
- `RELAY2=OFF\r`
- `DIO3=ON\r`
- `DIO1=TYPE DI ERROR\r` (si DIO1 est une entrée)

## Gestion des erreurs

### Erreurs de connexion
- Timeout de connexion : 10 secondes
- Timeout d'authentification : 5 secondes
- Reconnexion automatique en cas de perte

### Erreurs de commandes
- `ERROR=GPIOERROR` : Service GPIO non disponible
- `DIO1=TYPE DI ERROR` : Tentative d'écriture sur une entrée
- `DIO1=SET ERROR` : Erreur générique de configuration

### Logs de débogage

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.rmg_rio4: debug
```

## Tests

### Script de test basique
```bash
python3 test_connection.py IP PORT USERNAME PASSWORD
```

### Script de test complet
```bash
python3 test_full.py IP PORT USERNAME PASSWORD
```

## Service personnalisé

### Service PULSE

Le service `rmg_rio4.pulse_relay` permet des impulsions temporaires :

```yaml
service: rmg_rio4.pulse_relay
data:
  entity_id: switch.relais_1
  duration: 2.5
```

**Implémentation :**
1. Récupère l'entity_id et la durée
2. Extrait le numéro de relais
3. Envoie `RELAYx PULSE durée`

## Développement

### Ajouter une nouvelle fonctionnalité

1. **Nouvelle commande** : Ajouter dans `RelayBoxConnection.send_command()`
2. **Nouveau message** : Ajouter dans `_process_message()`
3. **Nouvelle entité** : Créer une classe héritant de `SwitchEntity`
4. **Nouveau service** : Ajouter dans `services.yaml` et `__init__.py`

### Tests locaux

1. Modifier le code
2. Tester avec les scripts `test_*.py`
3. Vérifier les logs Home Assistant
4. Tester dans l'interface Home Assistant

### Debugging

1. Activer les logs debug
2. Utiliser `_LOGGER.debug()` pour tracer l'exécution
3. Vérifier les états des entités dans Home Assistant
4. Utiliser les outils développeur de HA

## Bonnes pratiques

### Gestion des états
- Toujours mettre à jour le cache local
- Notifier Home Assistant via `async_write_ha_state()`
- Éviter les doubles notifications

### Gestion des connexions
- Utiliser des timeouts appropriés
- Gérer les reconnexions automatiques
- Fermer proprement les connexions

### Gestion des erreurs
- Logger les erreurs avec le niveau approprié
- Informer l'utilisateur des problèmes
- Maintenir l'état `available` des entités

## Performance

### Optimisations
- Cache des états pour éviter les requêtes inutiles
- Polling intelligent (500ms dans le serveur)
- Commandes asynchrones pour éviter le blocage
- Timeouts courts pour les opérations réseau

### Limites
- Maximum 5 clients simultanés (serveur)
- Pas de chiffrement des communications
- Dépendant de la stabilité du réseau local