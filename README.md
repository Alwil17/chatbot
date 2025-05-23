# Chatbot API avec Telegram et DynamoDB

Ce projet est une API de chatbot qui utilise Mistral AI pour générer des réponses, s'intègre avec Telegram, et stocke les conversations dans AWS DynamoDB.

## Prérequis

- Python 3.8+
- Un compte AWS avec accès à DynamoDB
- Un bot Telegram (créé via @BotFather)
- Une clé API Mistral AI

## Configuration

1. Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
ENV_NAME=development
AWS_REGION_NAME=<votre-region-aws>
DYNAMO_TABLE=<nom-de-votre-table-dynamodb>
AWS_PROFILE=<votre-profil-aws>
MISTRAL_API_KEY=<votre-cle-api-mistral>
TELEGRAM_BOT_TOKEN=<votre-token-bot-telegram>
TELEGRAM_WEBHOOK_URL=<url-de-votre-api>
```

2. Créez une table DynamoDB avec la structure suivante :
   - Clé primaire : `id` (String)
   - Index secondaire global (GSI) :
     - Nom : `conversation_id-timestamp-index`
     - Clé de partition : `conversation_id`
     - Clé de tri : `timestamp`

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Démarrage

1. Lancez l'application localement :
```bash
uvicorn src.main:app --reload
```

2. Pour le développement, vous pouvez utiliser ngrok pour exposer votre API localement :
```bash
ngrok http 8000
```

3. Mettez à jour `TELEGRAM_WEBHOOK_URL` avec l'URL ngrok générée

## Utilisation

### API Endpoints

- `GET /` : Page d'accueil
- `GET /chat?question=<votre-question>&conversation_id=<id-optionnel>` : Envoyer une question au chatbot
- `GET /conversations/{conversation_id}` : Récupérer l'historique d'une conversation
- `POST /telegram/webhook` : Endpoint pour les webhooks Telegram

### Bot Telegram

1. Démarrez une conversation avec votre bot sur Telegram
2. Utilisez la commande `/start` pour commencer
3. Envoyez des messages normaux pour interagir avec le chatbot

## Structure du Projet

```
├── src/
│   ├── __init__.py
│   ├── main.py           # Point d'entrée de l'application
│   ├── config.py         # Configuration et variables d'environnement
│   ├── utils.py          # Utilitaires et fonctions helper
│   └── telegram_bot.py   # Gestion du bot Telegram
├── tests/                # Tests unitaires
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

## Sécurité

- Assurez-vous que vos clés API et tokens sont sécurisés
- Utilisez HTTPS pour votre webhook
- Configurez correctement les permissions AWS 