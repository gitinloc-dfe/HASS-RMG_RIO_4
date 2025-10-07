# Guide de personnalisation des icônes - RMG Rio 4

## Icônes par défaut

L'intégration RMG Rio 4 utilise des icônes dynamiques qui changent automatiquement selon l'état :

### Relais
- **OFF** : `mdi:electric-switch` (interrupteur ouvert)
- **ON** : `mdi:electric-switch-closed` (interrupteur fermé)

### DIO (Entrées digitales)
- **OFF** : `mdi:toggle-switch-off` (basculeur désactivé)
- **ON** : `mdi:toggle-switch` (basculeur activé)

## Personnaliser les icônes via Home Assistant

Vous pouvez personnaliser les icônes de vos entités directement dans l'interface Home Assistant :

### Méthode 1 : Via l'interface graphique

1. Allez dans **Paramètres** → **Appareils et services**
2. Trouvez votre intégration **RMG Rio 4**
3. Cliquez sur une entité (ex: `switch.relais_1`)
4. Cliquez sur l'icône ⚙️ (paramètres)
5. Dans le champ **Icône**, entrez votre icône personnalisée (ex: `mdi:garage`)
6. Cliquez **Mettre à jour**

### Méthode 2 : Via customize.yaml

Ajoutez dans votre `configuration.yaml` :

```yaml
homeassistant:
  customize: !include customize.yaml
```

Puis créez un fichier `customize.yaml` :

```yaml
# Personnalisation des relais
switch.relais_1:
  friendly_name: "Portail Principal"
  icon: mdi:garage

switch.relais_2:
  friendly_name: "Éclairage Extérieur"
  icon: mdi:lightbulb

switch.relais_3:
  friendly_name: "Sirène d'Alarme"
  icon: mdi:alarm-light

switch.relais_4:
  friendly_name: "Arrosage Automatique"
  icon: mdi:sprinkler

# Personnalisation des DIO
switch.dio_1:
  friendly_name: "Détecteur Véhicule"
  icon: mdi:car-connected

switch.dio_2:
  friendly_name: "Détecteur Mouvement"
  icon: mdi:motion-sensor

switch.dio_3:
  friendly_name: "Contact Porte"
  icon: mdi:door-open

switch.dio_4:
  friendly_name: "Capteur Humidité Sol"
  icon: mdi:water-percent
```

## Icônes recommandées par usage

### Portails et accès
- `mdi:garage` - Porte de garage
- `mdi:gate` - Portail
- `mdi:door-open` - Porte
- `mdi:barrier` - Barrière

### Éclairage
- `mdi:lightbulb` - Éclairage général
- `mdi:outdoor-lamp` - Éclairage extérieur
- `mdi:spotlight-beam` - Projecteur
- `mdi:string-lights` - Guirlandes

### Sécurité
- `mdi:alarm-light` - Sirène d'alarme
- `mdi:shield-home` - Système d'alarme
- `mdi:cctv` - Caméra de sécurité
- `mdi:motion-sensor` - Détecteur de mouvement

### Arrosage et jardin
- `mdi:sprinkler` - Arrosage automatique
- `mdi:water-pump` - Pompe
- `mdi:flower` - Zone plantée
- `mdi:grass` - Pelouse

### Capteurs
- `mdi:car-connected` - Détecteur véhicule
- `mdi:motion-sensor` - Détecteur mouvement
- `mdi:door-open` - Contact porte
- `mdi:water-percent` - Humidité
- `mdi:thermometer` - Température

### Équipements techniques
- `mdi:fan` - Ventilation
- `mdi:air-conditioner` - Climatisation
- `mdi:heat-pump` - Pompe à chaleur
- `mdi:electric-switch` - Interrupteur générique

## Icônes avec état dynamique

Si vous voulez conserver le changement d'icône selon l'état, utilisez des templates dans vos cartes Lovelace :

```yaml
type: entities
entities:
  - entity: switch.relais_1
    name: "Portail"
    icon: >-
      {% if is_state('switch.relais_1', 'on') %}
        mdi:garage-open
      {% else %}
        mdi:garage
      {% endif %}
```

## Ressources

- **Icônes Material Design** : https://materialdesignicons.com/
- **Documentation Home Assistant** : https://www.home-assistant.io/docs/configuration/customizing-entities/
- **Guide Lovelace** : https://www.home-assistant.io/lovelace/