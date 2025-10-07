# Exemples d'automatisations

## Portail électrique avec impulsion

Ouverture du portail avec une impulsion de 500ms :

```yaml
automation:
  - alias: "Ouvrir le portail avec un bouton"
    trigger:
      - platform: state
        entity_id: input_button.ouvrir_portail
        to: "on"
    action:
      - service: rmg_rio4.pulse_relay
        data:
          entity_id: switch.relais_1
          duration: 0.5
```

## Porte de garage

Contrôle de la porte de garage avec détection de l'état :

```yaml
automation:
  - alias: "Ouvrir/Fermer garage"
    trigger:
      - platform: state
        entity_id: cover.garage
        to: "open"
    action:
      - service: rmg_rio4.pulse_relay
        data:
          entity_id: switch.relais_2
          duration: 1
```

## Sonnette connectée

Activation d'une sonnette pendant 3 secondes :

```yaml
automation:
  - alias: "Sonnette connectée"
    trigger:
      - platform: state
        entity_id: binary_sensor.bouton_sonnette
        to: "on"
    action:
      - service: rmg_rio4.pulse_relay
        data:
          entity_id: switch.relais_3
          duration: 3
```

## Éclairage extérieur temporaire

Allumer l'éclairage extérieur pendant 10 minutes via détection de mouvement :

```yaml
automation:
  - alias: "Éclairage extérieur auto"
    trigger:
      - platform: state
        entity_id: binary_sensor.mouvement_exterieur
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.relais_4
      - delay:
          minutes: 10
      - service: switch.turn_off
        target:
          entity_id: switch.relais_4
```

## Arrosage automatique

Activer l'arrosage tous les matins pendant 15 minutes :

```yaml
automation:
  - alias: "Arrosage automatique"
    trigger:
      - platform: time
        at: "06:00:00"
    condition:
      - condition: state
        entity_id: weather.home
        state: "sunny"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.relais_1
      - delay:
          minutes: 15
      - service: switch.turn_off
        target:
          entity_id: switch.relais_1
```

## Contrôle vocal avec Google Assistant / Alexa

Créez des scripts pour le contrôle vocal :

```yaml
script:
  ouvrir_portail:
    alias: "Ouvrir le portail"
    sequence:
      - service: rmg_rio4.pulse_relay
        data:
          entity_id: switch.relais_1
          duration: 0.5

  ouvrir_garage:
    alias: "Ouvrir le garage"
    sequence:
      - service: rmg_rio4.pulse_relay
        data:
          entity_id: switch.relais_2
          duration: 1
```

Ensuite, exposez ces scripts à votre assistant vocal dans les paramètres d'intégration.

## Notification mobile en cas d'activation

Recevoir une notification quand un relais est activé :

```yaml
automation:
  - alias: "Notification portail ouvert"
    trigger:
      - platform: state
        entity_id: switch.relais_1
        to: "on"
    action:
      - service: notify.mobile_app_votre_telephone
        data:
          title: "Portail"
          message: "Le portail a été activé"
```

## Sécurité : Désactivation automatique

Pour éviter qu'un relais reste actif trop longtemps :

```yaml
automation:
  - alias: "Sécurité relais 3"
    trigger:
      - platform: state
        entity_id: switch.relais_3
        to: "on"
        for:
          minutes: 30
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.relais_3
      - service: notify.mobile_app_votre_telephone
        data:
          title: "Sécurité"
          message: "Le relais 3 est resté actif 30 min, désactivation automatique"
```

## Dashboard Lovelace

Exemple de carte pour contrôler vos relais :

```yaml
type: entities
title: Contrôle RMG RIO 4
entities:
  - entity: switch.relais_1
    name: Portail
    icon: mdi:gate
  - entity: switch.relais_2
    name: Garage
    icon: mdi:garage
  - entity: switch.relais_3
    name: Sonnette
    icon: mdi:bell
  - entity: switch.relais_4
    name: Éclairage
    icon: mdi:lightbulb
```

Avec boutons d'action :

```yaml
type: vertical-stack
cards:
  - type: button
    name: Ouvrir Portail
    icon: mdi:gate-open
    tap_action:
      action: call-service
      service: rmg_rio4.pulse_relay
      service_data:
        entity_id: switch.relais_1
        duration: 0.5
  - type: button
    name: Ouvrir Garage
    icon: mdi:garage-open
    tap_action:
      action: call-service
      service: rmg_rio4.pulse_relay
      service_data:
        entity_id: switch.relais_2
        duration: 1
```