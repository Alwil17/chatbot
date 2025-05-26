#!/usr/bin/env python3
import os
import sys
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def setup_dynamodb():
    """
    Crée la table DynamoDB si elle n'existe pas déjà.
    Configure les index secondaires nécessaires.
    """
    # Récupérer les credentials depuis les variables d'environnement
    table_name = os.getenv('DYNAMODB_TABLE_NAME')
    if not table_name:
        print("Erreur: DYNAMODB_TABLE_NAME non défini dans .env")
        sys.exit(1)

    try:
        # Créer le client DynamoDB
        dynamodb = boto3.client('dynamodb')

        # Vérifier si la table existe déjà
        try:
            dynamodb.describe_table(TableName=table_name)
            print(f"La table {table_name} existe déjà")
            return
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise e

        # Créer la table avec les configurations nécessaires
        print(f"Création de la table {table_name}...")
        response = dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'conversation_id-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'conversation_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        print("Attente de la création de la table...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        print("Table créée avec succès!")

    except ClientError as e:
        print(f"Erreur lors de la création de la table: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_dynamodb() 