# Guide de contribution

Merci de votre intérêt pour contribuer à HASS-RMG-RIO-4 ! 🎉

## Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [issues](https://github.com/gitinloc-dfe/HASS-RMG_RIO_4.git/issues)
2. Utilisez le template de bug report
3. Incluez autant de détails que possible :
   - Version de Home Assistant
   - Version de l'intégration
   - Logs pertinents
   - Étapes pour reproduire

### Suggérer une fonctionnalité

1. Vérifiez que la fonctionnalité n'a pas déjà été suggérée
2. Utilisez le template de feature request
3. Expliquez clairement :
   - Le problème que cela résoudrait
   - Comment vous l'utiliseriez
   - Des exemples d'utilisation

### Soumettre une Pull Request

1. **Fork le projet**
   ```bash
   git clone https://github.com/VOTRE-USERNAME/HASS-RMG-RIO-4.git
   cd HASS-RMG-RIO-4
   ```

2. **Créez une branche pour votre fonctionnalité**
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```

3. **Faites vos modifications**
   - Suivez le style de code existant
   - Ajoutez des commentaires si nécessaire
   - Testez vos modifications

4. **Committez vos changements**
   ```bash
   git add .
   git commit -m "feat: Description claire de la fonctionnalité"
   ```

5. **Poussez vers votre fork**
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```

6. **Ouvrez une Pull Request**
   - Décrivez clairement vos modifications
   - Référencez les issues liées
   - Attendez la revue de code

## Style de code

### Python

- Suivez [PEP 8](https://pep8.org/)
- Utilisez des noms de variables descriptifs
- Ajoutez des docstrings pour les fonctions et classes
- Limitez les lignes à 88 caractères (Black formatter)

**Exemple** :
```python
async def send_command(self, command: str) -> bool:
    """
    Envoie une commande au boîtier.
    
    Args:
        command: La commande à envoyer (ex: "RELAY1 ON")
        
    Returns:
        True si la commande a été envoyée avec succès, False sinon
    """
    if not self.connected:
        _LOGGER.error("Non connecté au boîtier")
        return False
    
    try:
        self.writer.write(f"{command}\r".encode('utf-8'))
        await self.writer.drain()
        return True
    except Exception as e:
        _LOGGER.error(f"Erreur: {e}")
        return False
```

### Convention de nommage

- **Classes** : `PascalCase` (ex: `RelayBoxConnection`)
- **Fonctions/Méthodes** : `snake_case` (ex: `send_command`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `DOMAIN`)
- **Variables** : `snake_case` (ex: `relay_name`)

### Logs

Utilisez les niveaux de log appropriés :
- `_LOGGER.debug()` : Informations de débogage détaillées
- `_LOGGER.info()` : Événements importants
- `_LOGGER.warning()` : Situations anormales mais gérables
- `_LOGGER.error()` : Erreurs qui empêchent une fonctionnalité
- `_LOGGER.critical()` : Erreurs graves

## Tests

### Tests locaux

1. **Installez l'intégration dans Home Assistant**
   ```bash
   cp -r custom_components/rmg_rio4 /config/custom_components/
   ```

2. **Redémarrez Home Assistant**

3. **Testez les fonctionnalités**
   - Configuration via l'interface
   - Activation/Désactivation des relais
   - Service PULSE
   - Reconnexion après perte de connexion

### Checklist avant de soumettre

- [ ] Le code fonctionne sans erreurs
- [ ] Les logs sont appropriés
- [ ] La documentation est à jour
- [ ] Les exemples fonctionnent
- [ ] Pas de mots de passe ou données sensibles dans le code
- [ ] Le CHANGELOG est mis à jour

## Structure des commits

Utilisez des messages de commit clairs suivant la convention [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>(<scope>): <description>

[corps optionnel]

[pied de page optionnel]
```

### Types de commit

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Modification de documentation
- `style`: Formatage, points-virgules manquants, etc.
- `refactor`: Refactorisation du code
- `test`: Ajout ou modification de tests
- `chore`: Mise à jour de tâches de build, config, etc.

**Exemples** :
```
feat(switch): ajout du support des DIO en tant que binary_sensors
fix(connection): correction de la reconnexion automatique
docs(readme): ajout d'exemples d'automatisations
```

## Documentation

Si vous ajoutez une nouvelle fonctionnalité, mettez à jour :

1. **README.md** : Ajoutez la description de la fonctionnalité
2. **EXAMPLES.md** : Ajoutez des exemples d'utilisation
3. **CHANGELOG.md** : Documentez le changement
4. **strings.json** : Ajoutez les traductions si nécessaire

## Questions ?

N'hésitez pas à :
- Ouvrir une [issue](https://github.com/gitinloc-dfe/HASS-RMG_RIO_4.git/issues) pour poser des questions
- Discuter dans les Pull Requests
- Consulter la [documentation du protocole](docs/PROTOCOL.md)

## Code de conduite

Soyez respectueux et courtois envers les autres contributeurs. Ce projet suit le [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## Licence

En contribuant, vous acceptez que vos contributions soient sous licence MIT, la même que ce projet.

Merci pour votre contribution ! 🙏