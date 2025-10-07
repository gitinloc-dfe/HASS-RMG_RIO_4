# RMG RIO 4 pour Home Assistant

Contrôlez votre boîtier RMG RIO 4 directement depuis Home Assistant !

## Fonctionnalités principales

- ✅ **Connexion TCP persistante** - Communication stable avec le boîtier
- ✅ **Contrôle ON/OFF** - Activation et désactivation des relais
- ✅ **Mode PULSE** - Impulsions temporaires configurables
- ✅ **Mises à jour en temps réel** - Les états se synchronisent automatiquement
- ✅ **Configuration graphique** - Pas besoin d'éditer des fichiers YAML
- ✅ **Support multi-relais** - Gérez jusqu'à 16 relais

## Configuration rapide

1. Ajoutez l'intégration via **Paramètres** → **Appareils et services**
2. Entrez l'IP de votre boîtier et vos identifiants
3. C'est prêt ! Vos relais apparaissent comme des switches

## Service PULSE

Utilisez le service `rmg_rio4.pulse_relay` pour des impulsions temporaires :

```yaml
service: rmg_rio4.pulse_relay
data:
  entity_id: switch.relais_1
  duration: 2.5  # secondes
```

Parfait pour les portails, portes de garage, sonnettes, etc.

## Support

Des questions ? Des problèmes ? Consultez le [README complet](https://github.com/gitinloc-dfe/HASS-RMG_RIO_4.git) ou ouvrez une [issue](https://github.com/gitinloc-dfe/HASS-RMG_RIO_4.git/issues).