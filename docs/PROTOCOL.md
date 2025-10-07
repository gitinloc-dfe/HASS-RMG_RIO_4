# Protocole de communication RMG RIO 4

Ce document décrit le protocole de communication TCP utilisé par le boîtier RMG RIO 4.

## Connexion

### Paramètres de connexion
- **Protocole** : TCP
- **Port** : 22023
- **Encodage** : UTF-8
- **Terminaison de ligne** : `\r` (Carriage Return)

### Établissement de la connexion

1. Le client se connecte au serveur TCP sur le port 22023
2. Le serveur envoie une demande d'authentification
3. Le client envoie ses identifiants
4. Le serveur confirme l'authentification

```
Client → Serveur : [Connexion TCP]
Serveur → Client : LOGINREQUEST?\r
Client → Serveur : admin;Inloc+1300\r
Serveur → Client : AUTHENTICATION=Successful\r
```

### Format d'authentification

```
<username>;<password>\r
```

**Exemple** : `admin;Inloc+1300\r`

## Commandes

Toutes les commandes se terminent par `\r`.

### Activer un relais

**Format** : `RELAY<N> ON\r`

**Exemple** :
```
Client → Serveur : RELAY1 ON\r
Serveur → Client : RELAY1=ON\r
```

### Désactiver un relais

**Format** : `RELAY<N> OFF\r`

**Exemple** :
```
Client → Serveur : RELAY3 OFF\r
Serveur → Client : RELAY3=OFF\r
```

### Mode PULSE (Impulsion)

Active le relais pendant une durée déterminée puis le désactive automatiquement.

**Format** : `RELAY<N> PULSE <durée>\r`

La durée est exprimée en secondes (accepte les décimales).

**Exemples** :
```
Client → Serveur : RELAY1 PULSE 0.5\r
Serveur → Client : RELAY1=ON\r
... [après 0.5 seconde] ...
Serveur → Client : RELAY1=OFF\r
```

```
Client → Serveur : RELAY2 PULSE 2.5\r
Serveur → Client : RELAY2=ON\r
... [après 2.5 secondes] ...
Serveur → Client : RELAY2=OFF\r
```

## Notifications d'état

Le serveur envoie automatiquement les changements d'état sans que le client ne les demande.

### Format des notifications

**Relais** : `RELAY<N>=<ÉTAT>\r`  
**DIO** : `DIO<N>=<ÉTAT>\r`

où `<ÉTAT>` peut être `ON` ou `OFF`.

**Exemple** :
```
Serveur → Client : RELAY1=ON\r
Serveur → Client : RELAY2=OFF\r
Serveur → Client : DIO1=OFF\r
Serveur → Client : DIO2=OFF\r
```

## État initial

Après l'authentification réussie, le serveur envoie l'état de tous les relais et DIOs :

```
Serveur → Client : AUTHENTICATION=Successful\r
Serveur → Client : RELAY1=OFF\r
Serveur → Client : RELAY2=OFF\r
Serveur → Client : RELAY3=OFF\r
Serveur → Client : RELAY4=OFF\r
Serveur → Client : DIO1=OFF\r
Serveur → Client : DIO2=OFF\r
Serveur → Client : DIO3=OFF\r
Serveur → Client : DIO4=OFF\r
```

## Gestion des erreurs

### Authentification échouée

```
Serveur → Client : AUTHENTICATION=Failed\r
```

La connexion est ensuite fermée par le serveur.

### Commande invalide

Le serveur peut ne pas répondre ou fermer la connexion si une commande est invalide.

## Maintien de la connexion

- La connexion reste ouverte en permanence
- Le serveur envoie les changements d'état en temps réel
- Il n'y a pas de mécanisme de keep-alive requis
- En cas de déconnexion, le client doit se reconnecter et s'authentifier à nouveau

## Notes techniques

### Délimiteurs
- Les commandes et réponses se terminent par `\r` (ASCII 13)
- Les lignes peuvent également contenir `\n` (ASCII 10) mais `\r` est le délimiteur principal

### Timing
- **Temps de réponse typique** : < 100ms
- **Durée minimale PULSE** : 0.1 seconde
- **Durée maximale PULSE recommandée** : 60 secondes

### Buffer de réception
Il est recommandé de :
- Utiliser un buffer pour accumuler les données reçues
- Parser les messages complets (délimités par `\r`)
- Gérer plusieurs messages dans le même paquet réseau

### Exemple de parsing

```python
buffer = ""
while True:
    data = socket.recv(1024)
    buffer += data.decode('utf-8')
    
    while '\r' in buffer:
        line, buffer = buffer.split('\r', 1)
        process_message(line.strip())
```

## Exemples de sessions complètes

### Session simple : Activer/Désactiver

```
# Connexion
Client → Serveur : [TCP connect]
Serveur → Client : LOGINREQUEST?\r
Client → Serveur : admin;Inloc+1300\r
Serveur → Client : AUTHENTICATION=Successful\r
Serveur → Client : RELAY1=OFF\r

# Activation
Client → Serveur : RELAY1 ON\r
Serveur → Client : RELAY1=ON\r

# Attente de 5 secondes

# Désactivation
Client → Serveur : RELAY1 OFF\r
Serveur → Client : RELAY1=OFF\r

# Déconnexion
Client → Serveur : [TCP disconnect]
```

### Session avec PULSE

```
# Connexion et authentification
Client → Serveur : [TCP connect]
Serveur → Client : LOGINREQUEST?\r
Client → Serveur : admin;Inloc+1300\r
Serveur → Client : AUTHENTICATION=Successful\r

# Commande PULSE
Client → Serveur : RELAY2 PULSE 1.5\r
Serveur → Client : RELAY2=ON\r
# [après 1.5 seconde]
Serveur → Client : RELAY2=OFF\r
```

## Compatibilité

Ce protocole est compatible avec :
- RMG RIO 4
- Firmware version : [À compléter selon votre modèle]

## Références

- Port par défaut : 22023
- Encodage : UTF-8
- Séparateur d'authentification : `;`
- Terminaison : `\r` (Carriage Return)