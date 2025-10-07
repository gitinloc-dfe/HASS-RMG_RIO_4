# Guide de démarrage rapide - Création du dépôt HASS-RMG-RIO-4

Ce guide vous accompagne étape par étape pour créer et publier votre dépôt GitHub.

## Étape 1 : Préparer les fichiers localement

### 1.1 Créer la structure de dossiers

```bash
# Créer le dossier principal
mkdir HASS-RMG-RIO-4
cd HASS-RMG-RIO-4

# Créer la structure
mkdir -p custom_components/rmg_rio4/translations
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p docs/images
```

### 1.2 Copier les fichiers Python

Créez ces fichiers dans `custom_components/rmg_rio4/` :

- ✅ `__init__.py` (code principal fourni)
- ✅ `config_flow.py` (interface de configuration)
- ✅ `switch.py` (plateforme switch)
- ✅ `manifest.json` (métadonnées)
- ✅ `services.yaml` (déclaration des services)
- ✅ `strings.json` (traductions)

### 1.3 Créer les fichiers racine

- ✅ `README.md` (documentation principale)
- ✅ `EXAMPLES.md` (exemples d'automatisations)
- ✅ `CHANGELOG.md` (journal des modifications)
- ✅ `CONTRIBUTING.md` (guide de contribution)
- ✅ `LICENSE` (licence MIT)
- ✅ `hacs.json` (configuration HACS)
- ✅ `info.md` (info HACS)
- ✅ `.gitignore` (fichiers à ignorer)

### 1.4 Créer les templates GitHub

Dans `.github/ISSUE_TEMPLATE/` :
- ✅ `bug_report.md`
- ✅ `feature_request.md`

### 1.5 Créer la documentation

Dans `docs/` :
- ✅ `PROTOCOL.md` (documentation du protocole)

## Étape 2 : Créer le dépôt sur GitHub

### 2.1 Aller sur GitHub

1. Connectez-vous à [github.com](https://github.com)
2. Cliquez sur le bouton **"+"** en haut à droite
3