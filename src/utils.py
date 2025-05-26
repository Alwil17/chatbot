import json
import logging
import os
from typing import List, Any, Dict
from logging import Logger

import boto3
from boto3.dynamodb.conditions import Key

from src.config import env_vars


class Utils:

    ALLOWED_EXTENSIONS = ["pdf", "docx", "doc", "png", "jpg", "jpeg"]

    @staticmethod
    def log_info(message: str) -> None:
        """_summary_
        Log a simple info message
        """
        logging.getLogger("uvicorn.error").info(msg=f"==> {message}")

    @staticmethod
    def log_debug(message: str) -> None:
        """_summary_
        Log a debug message
        """
        logging.getLogger("uvicorn.error").debug(msg=f"==> {message}")

    @staticmethod
    def log_error(message: str) -> None:
        """_summary_
        Log an error message
        """
        logging.getLogger("uvicorn.error").error(msg=f"==> {message}")

    @staticmethod
    def log_list(elements: List[Any]) -> None:
        if elements:
            logging.getLogger("uvicorn.error").info(
                msg=f"Displaying all the {len(elements)} elements of the list"
            )
            for i in range(len(elements)):
                logging.getLogger("uvicorn.error").info(
                    msg=f"##### {i} ==> {json.dumps(elements[i], indent=4)}"
                )

    @staticmethod
    def get_logger() -> Logger:
        return logging.getLogger("uvicorn.error")

    @staticmethod
    def get_dynamo_client() -> boto3.client:
        """Get DynamoDB client with appropriate credentials"""
        # Check if running in Lambda
        is_lambda = bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
        Utils.log_info(f"Running in Lambda environment: {is_lambda}")
        Utils.log_info(f"AWS Region: {env_vars.AWS_REGION_NAME}")
        Utils.log_info(f"DynamoDB Table: {env_vars.DYNAMO_TABLE}")

        if is_lambda:
            # In Lambda, use the role credentials
            Utils.log_info("Using Lambda IAM role credentials")
            return boto3.client("dynamodb", region_name=env_vars.AWS_REGION_NAME)
        else:
            # Local development - use explicit credentials
            Utils.log_info("Using local development credentials")
            return boto3.client(
                "dynamodb",
                region_name=env_vars.AWS_REGION_NAME,
                aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY,
            )

    @staticmethod
    def get_dynamo_resource() -> boto3.resource:
        """Get DynamoDB resource with appropriate credentials"""
        # Check if running in Lambda
        if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            # In Lambda, use the role credentials
            return boto3.resource("dynamodb", region_name=env_vars.AWS_REGION_NAME)
        else:
            # Local development - use explicit credentials
            return boto3.resource(
                "dynamodb",
                region_name=env_vars.AWS_REGION_NAME,
                aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY,
            )

    @staticmethod
    def insert_data(item: Dict[str, Dict[str, str]]) -> bool:
        try:
            Utils.log_info(f"Tentative d'insertion dans DynamoDB: {json.dumps(item, indent=2)}")
            dynamo_client = Utils.get_dynamo_client()
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
    def get_conversation_messages(conversation_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les messages d'une conversation spécifique"""
        dynamo_resource = Utils.get_dynamo_resource()
        table = dynamo_resource.Table(env_vars.DYNAMO_TABLE)

        response = table.query(
            IndexName="conversation_id-timestamp-index",  # l'index DynamoDB doit exister
            KeyConditionExpression=Key("conversation_id").eq(conversation_id),
            ScanIndexForward=True,  # Trier par timestamp croissant
        )

        items: List[Dict[str, Any]] = response.get("Items", [])
        return items

    @staticmethod
    def get_user_conversations(user_id: str) -> list:
        """Récupère toutes les conversations d'un utilisateur en utilisant l'index"""
        dynamo_resource = Utils.get_dynamo_resource()
        table = dynamo_resource.Table(env_vars.DYNAMO_TABLE)

        # Utilise une requête sur l'index avec le user_id
        response = table.query(
            IndexName="user_id-timestamp-index",  # Vous devrez créer cet index
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,  # Pour avoir les conversations les plus récentes en premier
        )

        # Groupe les messages par conversation_id
        conversations: Dict[str, Dict[str, Any]] = {}
        for item in response.get("Items", []):
            conv_id = item.get("conversation_id")
            if conv_id not in conversations:
                conversations[conv_id] = {
                    "conversation_id": conv_id,
                    "last_message": item.get("timestamp"),
                    "messages_count": 1,
                }
            else:
                conversations[conv_id]["messages_count"] += 1

        return list(conversations.values())

    @staticmethod
    def delete_conversation_messages(conversation_id: str) -> bool:
        """Supprime tous les messages d'une conversation spécifique"""
        try:
            # Récupérer d'abord tous les messages de la conversation
            messages = Utils.get_conversation_messages(conversation_id)

            if not messages:
                Utils.log_info(f"Aucun message à supprimer pour la conversation {conversation_id}")
                return True

            dynamo_resource = Utils.get_dynamo_resource()
            table = dynamo_resource.Table(env_vars.DYNAMO_TABLE)

            # Supprimer chaque message
            with table.batch_writer() as batch:
                for message in messages:
                    batch.delete_item(Key={"id": message["id"]})

            Utils.log_info(
                f"Suppression réussie de {len(messages)} messages. ID: {conversation_id}"
            )
            return True

        except Exception as e:
            Utils.log_error(
                f"Erreur lors de la suppression des messages {conversation_id}: {str(e)}"
            )
            raise e
