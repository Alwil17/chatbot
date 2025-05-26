# Guide de Démarrage Rapide

Ce guide vous permettra de démarrer rapidement avec le chatbot. Pour une documentation plus détaillée, consultez les autres fichiers dans le dossier `docs/`.

## Prérequis

- Python 3.8 ou supérieur
- Un compte AWS avec accès à DynamoDB
- Un bot Telegram (créé via @BotFather)
- Une clé API Mistral AI

## Installation Automatique (Recommandée)

1. **Clonez le dépôt**
   ```bash
   git clone https://github.com/Alwil17/chatbot.git
   cd chatbot
   ```

2. **Créez et activez l'environnement virtuel**
   ```bash
   python -m venv .venv
   # Sur Windows :
   .venv\Scripts\activate
   # Sur Linux/Mac :
   source .venv/bin/activate
   ```

3. **Lancez le script d'initialisation**
   ```bash
   python scripts/init.py
   ```

   Le script va automatiquement :
   - Vérifier la version de Python
   - Installer les dépendances
   - Configurer le fichier `.env`
   - Valider vos credentials AWS et Telegram
   - Créer la table DynamoDB
   - Configurer le webhook Telegram (optionnel)

## Installation Manuelle (Alternative)

Si vous préférez configurer chaque élément manuellement :

1. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurez l'environnement**
   ```bash
   cp .env.example .env
   # Éditez .env avec vos informations
   ```

3. **Créez la table DynamoDB**
   ```bash
   python scripts/setup_dynamodb.py
   ```

4. **Configurez le webhook Telegram**
   ```bash
   python scripts/set_webhook.py --url https://votre-url/telegram/webhook
   ```

## Démarrage du Bot

1. **En développement local**
   ```bash
   # Lancez ngrok pour le tunnel HTTPS
   ngrok http 8000

   # Dans un autre terminal, démarrez l'application
   uvicorn src.main:app --reload
   ```

2. **En production**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

## Test Rapide

1. **Via Telegram**
   - Ouvrez Telegram
   - Cherchez votre bot (@votre_bot_username)
   - Envoyez un message "Bonjour"

2. **Via l'API HTTP**
   ```bash
   curl "http://localhost:8000/chat?question=Bonjour"
   ```

## Commandes Telegram Disponibles

- `/start` - Démarre une nouvelle conversation
- `/help` - Affiche l'aide
- `/clear` - Efface l'historique de la conversation

## Structure des Fichiers Principaux

```
chatbot/
├── src/
│   ├── main.py           # Point d'entrée de l'application
│   ├── telegram_bot.py   # Logique du bot Telegram
│   └── utils.py          # Fonctions utilitaires
├── docs/                 # Documentation détaillée
└── tests/               # Tests unitaires et d'intégration
```

## Problèmes Courants

### Le bot ne répond pas
- Vérifiez que l'application est en cours d'exécution
- Vérifiez les logs pour les erreurs
- Assurez-vous que le webhook est correctement configuré

### Erreurs DynamoDB
- Vérifiez vos credentials AWS
- Assurez-vous que la table existe
- Vérifiez les permissions IAM

### Erreurs Mistral AI
- Vérifiez votre clé API
- Assurez-vous d'avoir du crédit disponible
- Vérifiez les limites de taux

## Prochaines Étapes

- Consultez [ARCHITECTURE.md](ARCHITECTURE.md) pour comprendre la structure
- Lisez [API.md](API.md) pour les détails de l'API
- Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour contribuer
- Consultez [DEPLOYMENT.md](DEPLOYMENT.md) pour le déploiement en production

## Besoin d'Aide ?

- Ouvrez une issue sur GitHub
- Consultez la documentation complète dans `docs/`
- Vérifiez les discussions existantes

---

Pour plus de détails sur chaque aspect, consultez la documentation correspondante dans le dossier `docs/`. 