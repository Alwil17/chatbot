# Guide de Contribution

Merci de votre intérêt pour contribuer !  
Nous accueillons toutes les améliorations, corrections de bugs, documentation et idées.

---

## Comment Contribuer

1. **Forkez le dépôt**  
   Cliquez sur le bouton "Fork" en haut à droite de cette page.

2. **Clonez votre fork**
   ```bash
   git clone https://github.com/Alwil17/chatbot.git
   cd chatbot
   ```

3. **Créez une nouvelle branche**
   ```bash
   git checkout -b ma-fonctionnalite
   ```

4. **Installez les dépendances**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
   pip install -r requirements.txt
   ```

5. **Configurez votre environnement**
   - Copiez `.env.example` vers `.env`
   - Remplissez avec vos identifiants AWS, clé API Mistral et token Telegram
   - Créez votre table DynamoDB en suivant les instructions du README

6. **Faites vos modifications**
   - Ajoutez des fonctionnalités, corrigez des bugs ou améliorez la documentation
   - Suivez le style et la structure du projet
   - Assurez-vous de ne jamais utiliser de scan DynamoDB

7. **Testez vos modifications**
   ```bash
   pytest
   ```

8. **Committez et poussez**
   ```bash
   git add .
   git commit -m "Description de votre modification"
   git push origin ma-fonctionnalite
   ```

9. **Ouvrez une Pull Request**
   - Allez sur votre fork sur GitHub
   - Cliquez sur "Compare & pull request"
   - Décrivez vos modifications et soumettez

---

## Convention de Nommage des Branches

- **Convention de nommage :**
  - Pour les nouvelles fonctionnalités : `feat/description-courte`
  - Pour les corrections de bugs : `bugfix/description-courte`
  - Pour la maintenance : `chore/description-courte`
  - Pour la documentation : `docs/description-courte`
  - Exemple :  
    ```
    git checkout -b feat/ajout-contexte-conversation
    git checkout -b bugfix/correction-webhook-telegram
    ```

- **Règles pour les Pull Requests :**
  - Utilisez un titre clair et descriptif (ex : `feat: ajout du support du contexte de conversation`)
  - Dans la description, expliquez **quoi** et **pourquoi**
  - Référencez les issues concernées si applicable (ex : `Résout #42`)
  - Assurez-vous que votre branche est à jour avec la branche cible (généralement `main`)
  - Vérifiez que tous les tests passent avant de demander une revue
  - Assignez des relecteurs si possible

---

## Style de Code et Bonnes Pratiques

- Suivez les conventions [PEP8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez les annotations de type et les docstrings
- Gardez les fonctions et classes concises et focalisées
- **Bonnes Pratiques DynamoDB :**
  - N'utilisez jamais de scan de table
  - Utilisez toujours des index pour les requêtes
  - Utilisez les opérations par lots quand possible
  - Gardez la taille des items réduite
- **Bonnes Pratiques Telegram :**
  - Gérez tous les types de messages possibles
  - Implémentez une gestion d'erreurs appropriée
  - Sécurisez les endpoints webhook
  - Utilisez le contexte de conversation de manière appropriée

---

## Tests

- Ajoutez ou mettez à jour les tests pour vos modifications
- Assurez-vous que tous les tests passent avec `pytest`
- Testez à la fois l'API et les fonctionnalités du bot Telegram
- Testez les opérations DynamoDB avec des réponses mockées
- Si vous ajoutez de nouveaux endpoints, ajoutez les tests correspondants dans `tests/`

---

## Documentation

- Mettez à jour le `README.md` ou les docstrings si votre modification affecte l'utilisation ou l'API
- Ajoutez des commentaires pour clarifier le code complexe
- Documentez toute nouvelle variable d'environnement
- Maintenez à jour la documentation de la structure de la table DynamoDB

---

## Suggestions et Problèmes

- Pour les demandes de fonctionnalités ou les rapports de bugs, veuillez [ouvrir une issue](https://github.com/Alwil17/chatbot/issues)
- Soyez clair et fournissez autant de contexte que possible
- Pour les problèmes DynamoDB, incluez la structure de la table et les patterns d'accès
- Pour les problèmes Telegram, incluez les logs des messages si possible

---

## Code de Conduite

Soyez respectueux et constructif.  
Consultez le fichier [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Notes Importantes

- Ne committez jamais d'informations sensibles (clés API, tokens, credentials)
- Ne committez jamais le fichier `.env`
- Testez toujours les opérations DynamoDB localement d'abord
- Faites attention aux URLs webhook en développement
- Prenez en compte les limites de taux pour les APIs Telegram et Mistral AI

---

Merci de nous aider à améliorer ce projet ! 🚀 