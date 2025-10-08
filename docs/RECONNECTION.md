# Reconnexion Automatique - RMG Rio 4

L'intégration RMG Rio 4 dispose d'un système de **reconnexion automatique robuste** pour gérer les interruptions de connexion de manière transparente.

## 🎯 Fonctionnalités

### ✅ **Détection automatique de déconnexion**
- **Surveillance continue** : Ping toutes les 30 secondes pour vérifier la santé de la connexion
- **Détection d'erreurs réseau** : Capture automatique des erreurs TCP (ConnectionError, BrokenPipeError, etc.)
- **Timeout intelligent** : Détection des connexions "zombies" (sans réponse > 60s)

### 🔄 **Stratégie de reconnexion intelligente**
- **Backoff exponentiel** : Délais progressifs entre tentatives
  - Tentative 1 : 5 secondes
  - Tentative 2 : 10 secondes  
  - Tentative 3 : 20 secondes
  - Tentative 4 : 40 secondes
  - Maximum : 5 minutes entre tentatives
- **Tentatives quasi-illimitées** : Continue jusqu'à retrouver la connexion
- **Reset automatique** : Remet les délais à zéro après connexion stable (30s)

### 📊 **Gestion d'état avancée**
- **Entités indisponibles** : Marquées automatiquement pendant les déconnexions
- **Retour automatique** : Redeviennent disponibles dès la reconnexion
- **Timeout d'entité** : Indisponibles si pas de mise à jour > 5 minutes
- **Indicateurs visuels** : État "Indisponible" dans l'interface Home Assistant

## 🛠️ Scénarios gérés automatiquement

### 1. **Redémarrage du RMG Rio 4**
```
[INFO] 🔌 Connexion fermée par le serveur
[INFO] 🔄 Tentative de reconnexion #1...
[INFO] ✅ Reconnexion réussie au RMG Rio 4
[INFO] 💓 Ping réussi - connexion stable
```

### 2. **Coupure réseau temporaire**
```
[WARNING] 💔 Ping échoué, connexion peut-être fermée
[INFO] 🔄 Tentative de reconnexion #1...
[INFO] ⏰ Prochaine tentative dans 5s
[INFO] 🔄 Tentative de reconnexion #2...
[INFO] ✅ Reconnexion réussie au RMG Rio 4
```

### 3. **Panne prolongée**
```
[WARNING] ❌ Reconnexion #5 échouée: [Errno 111] Connection refused
[INFO] ⏰ Prochaine tentative dans 80s
[INFO] DIO 1 indisponible
[INFO] Relais 1 indisponible
... (continue en arrière-plan) ...
```

### 4. **Redémarrage Home Assistant**
```
[INFO] 🔌 Connexion à 172.18.0.45:22023...
[INFO] ✅ Authentification réussie au RMG Rio 4  
[INFO] 🩺 Surveillance de connexion démarrée
```

## 🔧 Services disponibles

### Service `rmg_rio4.reconnect`
Force une reconnexion immédiate en cas de problème :

```yaml
service: rmg_rio4.reconnect
```

**Utilisation recommandée** :
- Après maintenance réseau
- Si les entités restent indisponibles
- Pour diagnostic de problèmes de connexion

### Service `rmg_rio4.pulse_relay` (amélioré)
Active un relais temporairement avec gestion d'erreur :

```yaml
service: rmg_rio4.pulse_relay
data:
  entity_id: switch.relais_1
  duration: 2.5
```

## 📈 Monitoring et diagnostic

### Dans les journaux Home Assistant
Recherchez ces patterns pour surveiller la santé :

```bash
# Connexion stable
💓 Ping réussi - connexion stable

# Problèmes détectés
💔 Ping échoué, connexion peut-être fermée
🚨 Connexion fermée détectée par surveillance

# Reconnexion en cours
🔄 Tentative de reconnexion #X...
⏰ Prochaine tentative dans Xs

# Succès
✅ Reconnexion réussie au RMG Rio 4
```

### Codes de statut des entités
- **Disponible** : Connexion active, communication normale
- **Indisponible** : Pas de connexion ou timeout > 5 minutes
- **Erreur de commande** : Connexion OK mais commande échouée

## ⚙️ Configuration avancée

Les paramètres suivants peuvent être ajustés dans le code si nécessaire :

```python
# Dans __init__.py, classe RelayBoxConnection
self._ping_interval = 30          # Ping toutes les 30s
self._max_reconnect_interval = 300 # Max 5 minutes entre tentatives
self._connection_stable_time = 30  # Stable après 30s

# Dans switch.py, propriété available
timedelta(minutes=5)  # Timeout entité après 5 minutes
```

## 🎯 Avantages

1. **Transparence** : Reconnexion invisible pour l'utilisateur
2. **Robustesse** : Gère tous les types de pannes réseau
3. **Performance** : Détection rapide des problèmes (30s max)
4. **Feedback** : Indicateurs visuels clairs dans Home Assistant
5. **Maintenance** : Service de reconnexion manuelle disponible

Cette implémentation assure une **disponibilité maximale** de votre système domotique RMG Rio 4 ! 🚀