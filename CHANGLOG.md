# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### À venir
- Support des entrées DIO en tant que binary_sensors
- Reconnexion automatique en cas de perte de connexion
- Support des notifications de changement d'état

## [1.0.0] - 2025-10-07

### Ajouté
- Connexion TCP au boîtier RMG RIO 4 sur le port 22023
- Authentification automatique avec login/mot de passe
- Support des commandes ON/OFF pour les relais
- Support du mode PULSE avec durée configurable
- Configuration via l'interface graphique de Home Assistant
- Service `rmg_rio4.pulse_relay` pour les impulsions temporaires
- Création automatique des entités switch pour chaque relais
- Mise à jour en temps réel des états des relais
- Traductions en français et anglais
- Documentation complète avec exemples

### Testé avec
- Home Assistant 2023.1.0 et supérieur
- RMG RIO 4 avec firmware TCP

## Types de modifications

- `Ajouté` pour les nouvelles fonctionnalités
- `Modifié` pour les changements dans les fonctionnalités existantes
- `Obsolète` pour les fonctionnalités bientôt supprimées
- `Supprimé` pour les fonctionnalités supprimées
- `Corrigé` pour les corrections de bugs
- `Sécurité` pour les vulnérabilités corrigées