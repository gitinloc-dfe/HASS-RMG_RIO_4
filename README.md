# HASS-RMG-RIO-4

Intégration Home Assistant pour le boîtier RMG RIO 4 (contrôle de rela### Icônes

L'intégration utilise des icônes Material Design Icons (MDI) qui changent automatiquement selon l'état :

- **Relais** : `mdi:electric-switch` (OFF) / `mdi:electric-switch-closed` (ON)
- **DIO** : `mdi:toggle-switch-off` (OFF) / `mdi:toggle-switch` (ON)

📖 **Guide complet de personnalisation** : [docs/ICONS.md](docs/ICONS.md)

### Icône du dépôt HACS

Pour personnaliser l'icône visible dans HACS :
1. Convertissez `assets/icon.svg` en PNG 256x256 pixels
2. Renommez le fichier en `icon.png`
3. Placez-le à la racine du dépôt
4. HACS détectera automatiquement la nouvelle icôneome Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.1-green.svg)

## Description

Cette intégration personnalisée permet de contrôler le boîtier **RMG RIO 4** via Home Assistant. Le boîtier communique en TCP sur le port 22023 et permet de piloter des relais et des sorties DIO.

## ✨ Fonctionnalités

- 🔌 **Connexion TCP** sécurisée avec authentification
- 🎛️ **4 relais** contrôlables (ON/OFF/PULSE)  
- 📊 **4 entrées/sorties digitales** (DIO)
- 🏠 **Intégration native** Home Assistant
- ⚡ **Service PULSE** pour activations temporaires
- 🌐 **Configuration via interface** graphique
- 📱 **Compatible HACS** pour installation facile
- 🔄 **Reconnexion automatique** robuste avec backoff exponentiel
- 💓 **Surveillance de santé** de connexion en temps réel
- 🛠️ **Service de reconnexion** manuelle pour maintenance  

## Installation

### Méthode HACS (recommandée)

1. Ouvrez HACS dans Home Assistant
2. Allez dans "Intégrations"
3. Cliquez sur les 3 points en haut à droite
4. Sélectionnez "Dépôts personnalisés"
5. Ajoutez l'URL : `https://github.com/gitinloc-dfe/HASS-RMG_RIO_4.git
6. Sélectionnez la catégorie "Integration"
7. Cliquez sur "Ajouter"
8. Recherchez "RMG RIO 4" et installez

### Méthode manuelle

1. Téléchargez le dossier `custom_components/rmg_rio4`
2. Copiez-le dans votre dossier `custom_components` de Home Assistant :
   ```
   config/
   └── custom_components/
       └── rmg_rio4/
           ├── __init__.py
           ├── config_flow.py
           ├── manifest.json
           ├── services.yaml
           ├── strings.json
           └── switch.py
   ```
3. Redémarrez Home Assistant

## Configuration

1. Allez dans **Paramètres** → **Appareils et services** → **Ajouter une intégration**
2. Recherchez **"RMG RIO 4"**
3. Remplissez les informations de connexion :
   - **Adresse IP** : L'adresse IP de votre boîtier (ex: `172.18.0.45`)
   - **Port TCP** : `22023` (par défaut)
   - **Nom d'utilisateur** : `admin` (par défaut)
   - **Mot de passe** : Votre mot de passe (ex: `numéro de série`)

   *Note : Le Rio 4 a toujours 4 relais et 4 DIO, pas besoin de le spécifier*

## Utilisation

### Contrôle des relais

Les relais apparaissent comme des entités `switch` dans Home Assistant :
- `switch.relais_1`
- `switch.relais_2`
- `switch.relais_3`
- `switch.relais_4`

### Commandes basiques

#### Activer/Désactiver un relais

```yaml
# Dans une automation ou un script
service: switch.turn_on
target:
  entity_id: switch.relais_1

service: switch.turn_off
target:
  entity_id: switch.relais_1
```

### Icônes dynamiques

L'intégration utilise des icônes qui changent selon l'état des entités :

#### Relais
- 🔌 `mdi:electric-switch` : Relais désactivé (OFF)
- 🔌 `mdi:electric-switch-closed` : Relais activé (ON)

#### DIO (Entrées digitales)
- 🎚️ `mdi:toggle-switch-off` : Entrée désactivée (OFF)
- 🎚️ `mdi:toggle-switch` : Entrée activée (ON)

#### DIO (Sorties digitales - si configurées)
- 🔌 `mdi:electric-switch` : Sortie désactivée (OFF)
- 🔌 `mdi:electric-switch-closed` : Sortie activée (ON)

### Services disponibles

#### Service PULSE : `rmg_rio4.pulse_relay`

Le service permet d'activer un relais pendant une durée définie puis de le désactiver automatiquement.

```yaml
# Impulsion de 2.5 secondes sur le relais 1
service: rmg_rio4.pulse_relay
data:
  entity_id: switch.relais_1
  duration: 2.5
```

#### Service de reconnexion : `rmg_rio4.reconnect`

Force une reconnexion immédiate en cas de problème de communication.

```yaml
service: rmg_rio4.reconnect
```

### Reconnexion automatique

L'intégration dispose d'un **système de reconnexion automatique robuste** :

- ✅ **Détection automatique** des déconnexions (ping toutes les 30s)
- 🔄 **Reconnexion intelligente** avec backoff exponentiel (5s → 5min max)
- 📊 **Gestion d'état avancée** (entités indisponibles pendant déconnexion)
- 🛠️ **Service de reconnexion manuelle** pour forcer une reconnexion

📖 **Guide complet** : [docs/RECONNECTION.md](docs/RECONNECTION.md)

#### Cas d'usage typique : Portail ou porte de garage

```yaml
automation:
  - alias: "Ouvrir le portail"
    trigger:
      - platform: state
        entity_id: binary_sensor.bouton_portail
        to: "on"
    action:
      - service: rmg_rio4.pulse_relay
        data:
          entity_id: switch.relais_1
          duration: 0.5  # Impulsion de 500ms
```

Pour plus d'exemples, consultez la [documentation Home Assistant sur les automatisations](https://www.home-assistant.io/docs/automation/).

## Protocole de communication

Le boîtier RMG RIO 4 utilise un protocole TCP texte simple :

### Authentification
```
← LOGINREQUEST?        # Le serveur demande l'authentification
→ admin;password\r     # Envoi des identifiants
← AUTHENTICATION=Successful
```

### Commandes disponibles

#### Contrôle des relais
```
→ RELAY1 ON\r          # Activer le relais 1
← RELAY1=ON            # Confirmation

→ RELAY1 OFF\r         # Désactiver le relais 1  
← RELAY1=OFF           # Confirmation

→ RELAY1 PULSE 2.5\r   # Impulsion de 2.5 secondes
← RELAY1=ON            # Activation immédiate
← RELAY1=OFF           # Désactivation automatique après 2.5s

→ RELAY1?\r            # Demander l'état du relais 1
← RELAY1=ON            # Réponse avec l'état actuel
```

#### Contrôle des DIO (Digital Input/Output)
```
→ DIO1?\r              # Demander l'état de DIO1
← DIO1=OFF             # Réponse

→ DIO1 ON\r            # Activer DIO1 (si c'est une sortie)
← DIO1=ON              # Confirmation
← DIO1=TYPE DI ERROR   # Erreur si c'est une entrée

→ DIO1 OFF\r           # Désactiver DIO1
← DIO1=OFF             # Confirmation
```

#### Informations système
```
→ SERIALNUMBER?\r      # Numéro de série
← SERIALNUMBER=xxxxx

→ FIRMWAREVERSION?\r   # Version du firmware
← FIRMWAREVERSION=x.x.x

→ HOSTNAME?\r          # Nom d'hôte
← HOSTNAME=RMG-xxxxx

→ GOODBYE!\r           # Fermeture propre
← BYEBYE!
```

### États automatiques
Le serveur envoie automatiquement :
1. **À la connexion** : tous les états actuels
2. **En temps réel** : tous les changements d'état

```
← RELAY1=ON
← RELAY2=OFF
← RELAY3=OFF
← RELAY4=OFF
← DIO1=OFF
← DIO2=ON
← DIO3=OFF
← DIO4=OFF
```

## Dépannage

### L'intégration ne se connecte pas

1. Vérifiez que l'adresse IP et le port sont corrects
2. Vérifiez que le mot de passe est correct (souvent le numéro de série du boîtier)
3. Testez la connectivité réseau : `ping IP_DU_BOITIER`
4. Vérifiez que le port 22023 n'est pas bloqué par un firewall
5. Consultez les logs de Home Assistant : **Paramètres** → **Système** → **Logs**

### Les états ne se mettent pas à jour

1. Vérifiez que la connexion TCP est toujours active
2. Redémarrez l'intégration depuis **Appareils et services**
3. Vérifiez les logs pour détecter les erreurs de communication

### Activer les logs de débogage

Ajoutez dans votre `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.rmg_rio4: debug
```

## Compatibilité

- **Home Assistant** : 2023.1 ou supérieur
- **Python** : 3.11 ou supérieur  
- **Boîtier** : RMG RIO 4 
- **Micrologiciel recommandé** : v1.1.4 ou supérieur
- **Protocole** : TCP sur port 22023

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour signaler un bug
- Proposer des améliorations
- Soumettre des pull requests

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Support

Pour toute question ou problème :
- Ouvrez une [issue sur GitHub](https://github.com/VOTRE-USERNAME/HASS-RMG-RIO-4/issues)
- Consultez la [documentation Home Assistant](https://www.home-assistant.io/)

## Auteur

Créé pour la communauté Home Assistant 🏠

---

**Note** : Cette intégration n'est pas officiellement supportée par RMG. C'est un projet communautaire indépendant.