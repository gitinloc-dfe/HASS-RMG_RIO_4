# Guide de dépannage HACS

## Problème : "Could not download, see log for details"

Ce message d'erreur peut avoir plusieurs causes. Voici comment le résoudre :

### 1. Vérification des prérequis HACS

Assurez-vous que :
- ✅ HACS est correctement installé et configuré dans Home Assistant
- ✅ Votre Home Assistant a accès à Internet
- ✅ Vous utilisez une version récente de HACS (>= 1.32.0 recommandé)

### 2. Installation manuelle (méthode alternative)

Si HACS ne fonctionne pas, utilisez l'installation manuelle :

```bash
# 1. Téléchargez le code depuis GitHub
wget https://github.com/gitinloc-dfe/HASS-RMG_RIO_4/archive/v1.0.0.zip

# 2. Décompressez dans votre dossier Home Assistant
unzip v1.0.0.zip
cp -r HASS-RMG_RIO_4-1.0.0/custom_components/rmg_rio4 /config/custom_components/

# 3. Redémarrez Home Assistant
```

### 3. Installation via Git

```bash
# Cloner directement dans custom_components
cd /config/custom_components
git clone https://github.com/gitinloc-dfe/HASS-RMG_RIO_4.git rmg_rio4_temp
cp -r rmg_rio4_temp/custom_components/rmg_rio4 .
rm -rf rmg_rio4_temp
```

### 4. Vérification de l'installation

Après installation, vérifiez la structure :

```
/config/custom_components/rmg_rio4/
├── __init__.py
├── config_flow.py
├── manifest.json
├── services.yaml
├── strings.json
├── switch.py
└── translations/
    ├── fr.json
    └── en.json
```

### 5. Test de fonctionnement

1. **Redémarrez Home Assistant**
2. **Vérifiez les logs** pour d'éventuelles erreurs
3. **Testez votre matériel** avec les scripts fournis :

```bash
# Téléchargez les scripts de test
wget https://raw.githubusercontent.com/gitinloc-dfe/HASS-RMG_RIO_4/v1.0.0/test_connection.py
python3 test_connection.py VOTRE_IP 22023 admin VOTRE_PASSWORD
```

### 6. Configuration dans Home Assistant

1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez **+ AJOUTER UNE INTÉGRATION**
3. Recherchez **"RMG RIO 4"**
4. Remplissez les informations de connexion

### 7. Résolution des erreurs courantes

#### Erreur : "Component not found"
- Vérifiez que le dossier `rmg_rio4` est dans `/config/custom_components/`
- Redémarrez Home Assistant

#### Erreur : "Cannot connect"
- Testez d'abord avec `test_connection.py`
- Vérifiez l'IP et le port (22023)
- Vérifiez les identifiants (admin/password)

#### Erreur : "Authentication failed"
- Vérifiez le mot de passe (souvent le numéro de série)
- Testez avec telnet : `telnet IP 22023`

### 8. Logs de débogage

Activez les logs détaillés :

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.rmg_rio4: debug
```

### 9. Support et aide

- 📖 **Documentation** : [GitHub Repository](https://github.com/gitinloc-dfe/HASS-RMG_RIO_4)
- 🐛 **Issues** : [Signaler un problème](https://github.com/gitinloc-dfe/HASS-RMG_RIO_4/issues)
- 💬 **Discussions** : [Communauté Home Assistant](https://community.home-assistant.io/)

### 10. Version testée

Cette intégration a été testée avec :
- **Home Assistant** : 2023.1+
- **HACS** : 1.32.0+
- **Hardware** : RMG Rio 4 (Firmware 1.1.4)
- **Python** : 3.11+

### 11. Alternative : Installation directe

Si rien ne fonctionne, copiez manuellement les fichiers :

1. Téléchargez le [release v1.0.0](https://github.com/gitinloc-dfe/HASS-RMG_RIO_4/releases/tag/v1.0.0)
2. Extrayez `custom_components/rmg_rio4/` dans votre dossier Home Assistant
3. Redémarrez
4. Ajoutez l'intégration via l'interface