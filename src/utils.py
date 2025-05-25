from datetime import datetime
import json
from uuid import uuid4
import logging
from typing import List

import boto3
from boto3.dynamodb.conditions import Key

from src.config import env_vars
## Simple edit


class Utils:

    ALLOWED_EXTENSIONS = ["pdf", "docx", "doc", "png", "jpg", "jpeg"]

    @staticmethod
    def log_info(message):
        """_summary_
        Log a simple info message
        """
        logging.getLogger("uvicorn.error").info(msg=f"==> {message}")

    @staticmethod
    def log_debug(message):
        """_summary_
        Log a debug message
        """
        logging.getLogger("uvicorn.error").debug(msg=f"==> {message}")

    @staticmethod
    def log_error(message):
        """_summary_
        Log an error message
        """
        logging.getLogger("uvicorn.error").error(msg=f"==> {message}")

    @staticmethod
    def log_list(elements: List[any]):
        if elements:
            logging.getLogger("uvicorn.error").info(
                msg=f"Displaying all the {len(elements)} elements of the list"
            )
            for i in range(len(elements)):
                logging.getLogger("uvicorn.error").info(
                    msg=f"##### {i} ==> {json.dumps(elements[i], indent=4)}"
                )

    @staticmethod
    def get_logger():
        return logging.getLogger("uvicorn.error")

    @staticmethod
    def get_session():
        return boto3.Session(
            region_name=env_vars.AWS_REGION_NAME, profile_name=env_vars.AWS_PROFILE
        )

    @staticmethod
    def insert_data(item):
        try:
            Utils.log_info(f"Tentative d'insertion dans DynamoDB: {json.dumps(item, indent=2)}")
            dynamo_client = boto3.client(
                "dynamodb",
                region_name=env_vars.AWS_REGION_NAME,
                aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY
            )
            dynamo_client.put_item(
                TableName=env_vars.DYNAMO_TABLE,
                Item=item,
            )
            Utils.log_info("Données insérées avec succès dans DynamoDB")
            return True
        except Exception as e:
            Utils.log_error(f"Erreur lors de l'insertion dans DynamoDB: {str(e)}")
            raise e

    @staticmethod
    def get_conversation_messages(conversation_id: str):
        """Récupère tous les messages d'une conversation spécifique"""
        dynamo_resource = boto3.resource(
            "dynamodb",
            region_name=env_vars.AWS_REGION_NAME,
            aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY
        )
        table = dynamo_resource.Table(env_vars.DYNAMO_TABLE)
        
        response = table.query(
            IndexName="conversation_id-timestamp-index",  # Vous devrez créer cet index dans DynamoDB
            KeyConditionExpression=Key("conversation_id").eq(conversation_id),
            ScanIndexForward=True  # Trier par timestamp croissant
        )
        
        return response.get("Items", [])

    @staticmethod
    def get_user_conversations(user_id: str):
        """Récupère toutes les conversations d'un utilisateur en utilisant l'index"""
        dynamo_resource = boto3.resource(
            "dynamodb",
            region_name=env_vars.AWS_REGION_NAME,
            aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY
        )
        table = dynamo_resource.Table(env_vars.DYNAMO_TABLE)
        
        # Utilise une requête sur l'index avec le user_id
        response = table.query(
            IndexName="user_id-timestamp-index",  # Vous devrez créer cet index
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False  # Pour avoir les conversations les plus récentes en premier
        )
        
        # Groupe les messages par conversation_id
        conversations = {}
        for item in response.get("Items", []):
            conv_id = item.get("conversation_id")
            if conv_id not in conversations:
                conversations[conv_id] = {
                    "conversation_id": conv_id,
                    "last_message": item.get("timestamp"),
                    "messages_count": 1
                }
            else:
                conversations[conv_id]["messages_count"] += 1
        
        return list(conversations.values())
