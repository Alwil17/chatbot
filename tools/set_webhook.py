#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def setup_webhook(webhook_url):
    """
    Configure le webhook Telegram pour le bot.
    
    Args:
        webhook_url (str): L'URL complète du webhook (https://...)
    """
    # Récupérer le token depuis les variables d'environnement
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("Erreur: TELEGRAM_BOT_TOKEN non défini dans .env")
        sys.exit(1)

    if not webhook_url.startswith('https://'):
        print("Erreur: L'URL du webhook doit commencer par https://")
        sys.exit(1)

    # URL de l'API Telegram pour configurer le webhook
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"

    try:
        # Vérifier d'abord le webhook actuel
        info_response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        )
        info_response.raise_for_status()
        current_webhook = info_response.json()
        
        if 'result' in current_webhook and 'url' in current_webhook['result']:
            current_url = current_webhook['result']['url']
            if current_url == webhook_url:
                print(f"Le webhook est déjà configuré sur {webhook_url}")
                return
            print(f"Modification du webhook: {current_url} → {webhook_url}")
        else:
            print(f"Configuration initiale du webhook sur {webhook_url}")

        # Configurer le nouveau webhook
        response = requests.post(
            api_url,
            json={'url': webhook_url}
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("Webhook configuré avec succès!")
        else:
            print(f"Erreur: {result.get('description', 'Erreur inconnue')}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la configuration du webhook: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Configure le webhook Telegram pour le bot')
    parser.add_argument('--url', required=True, help='URL du webhook (https://...)')
    args = parser.parse_args()
    
    setup_webhook(args.url)

if __name__ == "__main__":
    main() 