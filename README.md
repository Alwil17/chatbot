# Chatbot API avec Telegram et DynamoDB

Ce projet est une API de chatbot qui utilise Mistral AI pour générer des réponses, s'intègre avec Telegram, et stocke les conversations dans AWS DynamoDB.

## Prérequis

- Python 3.8+
- Un compte AWS avec accès à DynamoDB
- Un bot Telegram (ID: @grey_chat_bot)
- Une clé API Mistral AI

## Configuration

1. Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
ENV_NAME=development
AWS_REGION_NAME=<votre-region-aws>
DYNAMO_TABLE=<nom-de-votre-table-dynamodb>
AWS_ACCESS_KEY_ID=<votre-access-key-id>
AWS_SECRET_ACCESS_KEY=<votre-secret-access-key>
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

1. Recherchez `@grey_chat_bot` sur Telegram
2. Démarrez une conversation avec le bot
3. Utilisez la commande `/start` pour commencer
4. Envoyez des messages normaux pour interagir avec le chatbot

### Gestion des données

Pour vider la table en développement (réinitialiser les données) :

```bash
# Supprimer la table
aws dynamodb delete-table --table-name VOTRE_NOM_TABLE

# Attendre quelques secondes que la suppression soit effective

# Recréer la table avec la même structure
aws dynamodb create-table \
    --table-name VOTRE_NOM_TABLE \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=conversation_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"conversation_id-timestamp-index\",
                \"KeySchema\": [
                    {\"AttributeName\":\"conversation_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"timestamp\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                },
                \"ProvisionedThroughput\": {
                    \"ReadCapacityUnits\": 5,
                    \"WriteCapacityUnits\": 5
                }
            }
        ]"
```

⚠️ Note : Évitez d'utiliser "Delete items" dans la console AWS car cela effectue un scan complet de la table.

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
- Ne commitez jamais le fichier `.env` dans Git 