# Structure du dépôt HASS-RMG-RIO-4

Voici la structure complète de votre dépôt GitHub :

```
HASS-RMG_RIO_4/
│
├── custom_components/
│   └── rmg_rio4/
│       ├── __init__.py           # Point d'entrée principal
│       ├── config_flow.py        # Interface de configuration
│       ├── manifest.json         # Métadonnées de l'intégration
│       ├── services.yaml         # Déclaration des services
│       ├── strings.json          # Traductions
│       ├── switch.py             # Plateforme switch
│       └── translations/
│           ├── en.json           # Traductions anglaises
│           └── fr.json           # Traductions françaises
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md         # Template pour les bugs
│   │   └── feature_request.md    # Template pour les suggestions
│   └── workflows/
│       └── validate.yml          # CI/CD pour validation (optionnel)
│
├── docs/
│   ├── images/
│   │   ├── screenshot-config.png # Capture de la configuration
│   │   ├── screenshot-entities.png # Capture des entités
│   │   └── logo.png              # Logo de l'intégration
│   └── PROTOCOL.md               # Documentation du protocole TCP
│
├── .gitignore                    # Fichiers à ignorer
├── hacs.json                     # Configuration HACS
├── info.md                       # Info pour HACS
├── LICENSE                       # Licence MIT
├── README.md                     # Documentation principale
├── EXAMPLES.md                   # Exemples d'automatisations
└── CHANGELOG.md                  # Journal des modifications
```

## Description des fichiers principaux

### custom_components/rmg_rio4/

**`__init__.py`**
- Gère la connexion TCP au boîtier
- Classe `RelayBoxConnection` pour la communication
- Classe `RelaySwitch` pour les entités switch
- Enregistrement des services Home Assistant
- Gestion du cycle de vie de l'intégration

**`config_flow.py`**
- Interface de configuration graphique
- Validation de la connexion
- Gestion des erreurs d'authentification

**`manifest.json`**
- Métadonnées de l'intégration
- Version, nom, domaine
- Liens vers documentation et issues

**`services.yaml`**
- Déclaration du service `pulse_relay`
- Paramètres et leur validation

**`strings.json`**
- Textes de l'interface de configuration
- Messages d'erreur
- Labels des champs

**`switch.py`**
- Configuration de la plateforme switch
- Création des entités pour chaque relais

### Fichiers racine

**`README.md`**
- Documentation complète
- Instructions d'installation
- Guide d'utilisation
- Exemples de base

**`EXAMPLES.md`**
- Exemples d'automatisations
- Scripts utiles
- Configurations Lovelace

**`hacs.json`**
- Configuration pour HACS
- Métadonnées de l'intégration

**`info.md`**
- Information courte pour HACS
- Résumé des fonctionnalités

**`LICENSE`**
- Licence MIT

**`.gitignore`**
- Fichiers Python à ignorer
- Fichiers IDE
- Fichiers système

## Création du dépôt

### 1. Initialiser le dépôt

```bash
# Créer le dossier
mkdir HASS-RMG-RIO-4
cd HASS-RMG-RIO-4

# Initialiser Git
git init
```

### 2. Créer la structure

```bash
# Créer les dossiers
mkdir -p custom_components/rmg_rio4/translations
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p docs/images

# Copier vos fichiers Python dans custom_components/rmg_rio4/
```

### 3. Premier commit

```bash
# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - RMG RIO 4 integration for Home Assistant"

# Ajouter le remote (après avoir créé le dépôt sur GitHub)
git remote add origin https://github.com/VOTRE-USERNAME/HASS-RMG-RIO-4.git

# Pousser vers GitHub
git branch -M main
git push -u origin main
```

### 4. Créer les releases

Pour chaque version, créez un tag et une release :

```bash
# Créer un tag
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release"

# Pousser le tag
git push origin v1.0.0
```

Ensuite, allez sur GitHub → Releases → Create a new release et associez le tag.

## Configuration HACS

Pour que votre intégration soit compatible HACS :

1. Le fichier `hacs.json` doit être à la racine
2. Le dossier `custom_components/rmg_rio4/` doit contenir tous les fichiers nécessaires
3. Un fichier `info.md` à la racine pour la description
4. Des releases avec tags (v1.0.0, v1.1.0, etc.)

## Bonnes pratiques

### Versioning sémantique

- **MAJOR** (1.x.x) : Changements incompatibles
- **MINOR** (x.1.x) : Nouvelles fonctionnalités compatibles
- **PATCH** (x.x.1) : Corrections de bugs

### Changelog

Maintenez un fichier `CHANGELOG.md` à jour avec toutes les modifications :

```markdown
# Changelog

## [1.0.0] - 2025-10-07
### Added
- Connexion TCP au boîtier RMG RIO 4
- Support des commandes ON/OFF
- Support du mode PULSE
- Configuration via interface graphique
- Service pulse_relay

## [1.0.1] - 2025-10-15
### Fixed
- Correction de la reconnexion automatique
- Amélioration de la gestion des erreurs
```

### Documentation des issues

Créez des templates pour les issues dans `.github/ISSUE_TEMPLATE/`.

## Promotion de votre intégration

1. **Forum Home Assistant** : Annoncez votre intégration
2. **Reddit** : Postez sur r/homeassistant
3. **Discord Home Assistant** : Partagez dans les channels appropriés
4. **HACS** : Soumettez pour inclusion dans le store par défaut