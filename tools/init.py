#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from importlib.metadata import version, PackageNotFoundError
from dotenv import load_dotenv
from setup_dynamodb import setup_dynamodb
from set_webhook import setup_webhook

def check_python_version():
    """Vérifie que la version de Python est >= 3.8"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 ou supérieur est requis")
        print(f"Version actuelle: {platform.python_version()}")
        sys.exit(1)
    print(f"✅ Python {platform.python_version()} détecté")

def check_env_file():
    """Vérifie que le fichier .env existe et contient les variables requises"""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'TELEGRAM_BOT_TOKEN',
        'MISTRAL_API_KEY',
        'DYNAMODB_TABLE_NAME'
    ]
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("ℹ️ Création du fichier .env à partir de .env.example")
            with open('.env.example', 'r') as example, open('.env', 'w') as env:
                env.write(example.read())
        else:
            print("❌ Fichier .env manquant et pas de .env.example trouvé")
            sys.exit(1)
    
    load_dotenv()
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Variables d'environnement manquantes dans .env:")
        for var in missing_vars:
            print(f"  - {var}")
        sys.exit(1)
    print("✅ Configuration .env validée")

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    try:
        with open('requirements.txt') as f:
            requirements = [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith('#')
            ]
        
        missing_deps = []
        for req in requirements:
            # Extraire le nom du package (sans version)
            pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
            try:
                version(pkg_name)
            except PackageNotFoundError:
                missing_deps.append(req)
        
        if missing_deps:
            print("📦 Installation des dépendances manquantes...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dépendances installées")
        else:
            print("✅ Toutes les dépendances sont installées")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des dépendances: {str(e)}")
        sys.exit(1)

def check_aws_credentials():
    """Vérifie que les credentials AWS sont valides"""
    import boto3
    from botocore.exceptions import ClientError
    
    try:
        sts = boto3.client('sts')
        sts.get_caller_identity()
        print("✅ Credentials AWS validés")
    except ClientError as e:
        print("❌ Erreur avec les credentials AWS:")
        print(f"  {str(e)}")
        sys.exit(1)

def check_telegram_token():
    """Vérifie que le token Telegram est valide"""
    import requests
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ Bot Telegram validé: @{bot_info['username']}")
        else:
            print("❌ Token Telegram invalide")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du token Telegram: {str(e)}")
        sys.exit(1)

def main():
    """Script principal d'initialisation"""
    print("\n🚀 Initialisation du projet chatbot\n")

    print("1️⃣ Vérification des prérequis...")
    check_python_version()
    check_dependencies()
    check_env_file()
    
    print("\n2️⃣ Validation des credentials...")
    check_aws_credentials()
    check_telegram_token()
    
    print("\n3️⃣ Configuration de DynamoDB...")
    setup_dynamodb()
    
    print("\n4️⃣ Configuration du webhook Telegram...")
    webhook_url = input("URL du webhook (laissez vide pour ignorer): ").strip()
    if webhook_url:
        setup_webhook(webhook_url)
    else:
        print("ℹ️ Configuration du webhook ignorée")
    
    print("\n✨ Initialisation terminée avec succès!")
    print("""
🎉 Prochaines étapes:
1. Lancez le bot: uvicorn src.main:app --reload
2. Testez avec Telegram: envoyez un message à votre bot
3. Testez l'API: curl "http://localhost:8000/chat?question=Bonjour"
""")

if __name__ == "__main__":
    main() 