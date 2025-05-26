# Guide de Déploiement

## Prérequis

- Compte AWS avec accès à:
  - DynamoDB
  - IAM
  - (Optionnel) Lambda si déploiement serverless
- Bot Telegram créé via @BotFather
- Clé API Mistral AI
- Domaine pour le webhook HTTPS (production)

## Configuration Locale

1. **Environnement Python**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
   pip install -r requirements.txt
   ```

2. **Variables d'Environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos credentials
   ```

3. **DynamoDB**
   ```bash
   # Créer la table
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

## Déploiement en Production

### Option 1: Serveur Traditionnel

1. **Préparation du Serveur**
   ```bash
   # Installation des dépendances système
   sudo apt update
   sudo apt install python3.8 python3.8-venv nginx

   # Configuration du pare-feu
   sudo ufw allow 80
   sudo ufw allow 443
   ```

2. **Configuration Nginx**
   ```nginx
   server {
       listen 80;
       server_name votre-domaine.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **SSL avec Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d votre-domaine.com
   ```

4. **Démarrage de l'Application**
   ```bash
   # Installation de PM2
   npm install -g pm2

   # Démarrage de l'application
   pm2 start "uvicorn src.main:app --host 0.0.0.0 --port 8000" --name chatbot
   pm2 save
   ```

### Option 2: Déploiement Serverless (AWS Lambda)

1. **Préparation du Package**
   ```bash
   # Création du package de déploiement
   pip install --target ./package -r requirements.txt
   cd package
   zip -r ../lambda.zip .
   cd ..
   zip -g lambda.zip src/*
   ```

2. **Configuration Lambda**
   - Runtime: Python 3.8
   - Handler: src.main.handler
   - Mémoire: 256 MB minimum
   - Timeout: 30 secondes

3. **Configuration API Gateway**
   - Créer une nouvelle API REST
   - Configurer les routes
   - Activer CORS si nécessaire

## Configuration Telegram

1. **Webhook Setup**
   ```bash
   curl -F "url=https://votre-domaine.com/telegram/webhook" \
        https://api.telegram.org/bot<VOTRE_TOKEN>/setWebhook
   ```

2. **Vérification du Webhook**
   ```bash
   curl https://api.telegram.org/bot<VOTRE_TOKEN>/getWebhookInfo
   ```

## Monitoring

1. **Logs Application**
   ```bash
   # Avec PM2
   pm2 logs chatbot

   # Avec systemd
   journalctl -u chatbot
   ```

2. **Métriques AWS**
   - Configurer CloudWatch
   - Monitorer les métriques DynamoDB
   - Configurer des alertes

## Backup et Maintenance

1. **Backup DynamoDB**
   ```bash
   # Activation des backups continus
   aws dynamodb update-continuous-backups \
       --table-name VOTRE_NOM_TABLE \
       --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
   ```

2. **Rotation des Logs**
   ```bash
   # Configuration logrotate
   sudo nano /etc/logrotate.d/chatbot
   ```

## Sécurité

1. **Firewall**
   ```bash
   # Configuration UFW
   sudo ufw default deny incoming
   sudo ufw allow ssh
   sudo ufw allow http
   sudo ufw allow https
   sudo ufw enable
   ```

2. **Fail2Ban**
   ```bash
   sudo apt install fail2ban
   sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
   sudo systemctl restart fail2ban
   ```

## Troubleshooting

### Problèmes Courants

1. **Webhook Telegram ne répond pas**
   - Vérifier les logs Nginx
   - Vérifier le certificat SSL
   - Vérifier les permissions du port

2. **DynamoDB Throttling**
   - Augmenter les capacités provisionnées
   - Implémenter l'exponential backoff
   - Vérifier les patterns d'accès

3. **Erreurs Mistral AI**
   - Vérifier la validité de la clé API
   - Vérifier les quotas
   - Implémenter la gestion des erreurs 