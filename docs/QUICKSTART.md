# Guide de Démarrage Rapide

Ce guide vous permettra de démarrer rapidement avec le chatbot. Pour une documentation plus détaillée, consultez les autres fichiers dans le dossier `docs/`.

## Prérequis

- Python 3.8 ou supérieur
- Un compte AWS avec accès à DynamoDB
- Un bot Telegram (créé via @BotFather)
- Une clé API Mistral AI

## Installation en 5 Minutes

1. **Clonez le dépôt**
   ```bash
   git clone https://github.com/Alwil17/chatbot.git
   cd chatbot
   ```

2. **Créez l'environnement virtuel**
   ```bash
   python -m venv .venv
   # Sur Windows :
   .venv\Scripts\activate
   # Sur Linux/Mac :
   source .venv/bin/activate
   ```

3. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurez les variables d'environnement**
   ```bash
   # Copiez le fichier d'exemple
   cp .env.example .env
   
   # Éditez .env avec vos informations
   # Sur Windows :
   notepad .env
   # Sur Linux/Mac :
   nano .env
   ```

   Contenu minimal requis dans `.env` :
   ```
   AWS_ACCESS_KEY_ID=votre_access_key
   AWS_SECRET_ACCESS_KEY=votre_secret_key
   AWS_REGION=votre_region
   TELEGRAM_BOT_TOKEN=votre_token_bot
   MISTRAL_API_KEY=votre_cle_api
   DYNAMODB_TABLE_NAME=nom_de_votre_table
   ```

5. **Créez la table DynamoDB**
   ```bash
   # Utilisez le script de configuration
   python scripts/setup_dynamodb.py
   ```

## Démarrage du Bot

1. **Lancez l'application**
   ```bash
   uvicorn src.main:app --reload
   ```

2. **Configurez le webhook Telegram**
   ```bash
   # En développement local avec ngrok
   ngrok http 8000
   
   # Utilisez l'URL générée
   python scripts/set_webhook.py --url https://votre-url-ngrok/telegram/webhook
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