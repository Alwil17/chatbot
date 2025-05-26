import json
import logging
from typing import List, Any, Dict
from boto3.session import Session
from logging import Logger
import asyncio
import time
from botocore.config import Config

import boto3
from boto3.dynamodb.conditions import Key

from src.config import env_vars


class RateLimiter:
    """Limiteur de débit pour DynamoDB"""

    def __init__(self, max_requests: int, time_window: float = 1.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquérir une autorisation d'accès"""
        async with self._lock:
            now = time.time()
            # Nettoyer les anciennes requêtes
            self.requests = [req for req in self.requests if now - req < self.time_window]

            if len(self.requests) >= self.max_requests:
                # Attendre que le créneau le plus ancien soit libéré
                sleep_time = self.requests[0] + self.time_window - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                self.requests.pop(0)

            self.requests.append(now)


class Utils:
    _instance = None
    _dynamo_client = None
    _table_name = "conversations"
    _semaphore = asyncio.Semaphore(5)  # Limite à 5 connexions simultanées (WCU)
    _rate_limiter = RateLimiter(max_requests=5, time_window=1.0)  # 5 requêtes par seconde (RCU/WCU)

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
    def get_session() -> Session:
        return boto3.Session(
            region_name=env_vars.AWS_REGION_NAME, profile_name=env_vars.AWS_PROFILE
        )

    @classmethod
    def get_dynamo_client(cls):
        """Obtenir le client DynamoDB avec configuration optimisée"""
        if cls._dynamo_client is None:
            config = Config(
                max_pool_connections=10,  # Réduit à 10 connexions dans le pool
                retries=dict(max_attempts=3, mode="adaptive"),
            )
            cls._dynamo_client = boto3.client(
                "dynamodb",
                region_name=env_vars.AWS_REGION_NAME,
                aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY,
            )
        return cls._dynamo_client

    @classmethod
    async def insert_data(cls, item: Dict[str, Any]) -> None:
        """Insérer des données avec contrôle de concurrence"""
        async with cls._semaphore:
            await cls._rate_limiter.acquire()
            client = cls.get_dynamo_client()
            client.put_item(TableName=cls._table_name, Item=item)

    @classmethod
    async def get_conversation_messages(cls, conversation_id: str) -> list:
        """Récupérer les messages avec contrôle de concurrence"""
        async with cls._semaphore:
            await cls._rate_limiter.acquire()
            client = cls.get_dynamo_client()
            response = client.query(
                TableName=cls._table_name,
                KeyConditionExpression="conversation_id = :cid",
                ExpressionAttributeValues={":cid": {"S": conversation_id}},
            )
            return response.get("Items", [])

    @classmethod
    async def batch_write(cls, items: list) -> None:
        """Écriture par lots avec contrôle de concurrence"""
        async with cls._semaphore:
            await cls._rate_limiter.acquire()
            client = cls.get_dynamo_client()

            # Réduit à 5 items par lot pour respecter le WCU
            for i in range(0, len(items), 5):
                batch = items[i : i + 5]
                request_items = {
                    cls._table_name: [{"PutRequest": {"Item": item}} for item in batch]
                }
                await asyncio.sleep(1)  # Attendre 1 seconde entre chaque lot
                client.batch_write_item(RequestItems=request_items)

    @classmethod
    def configure_table_throughput(cls, read_capacity: int = 1000, write_capacity: int = 1000):
        """Configurer la capacité de la table"""
        client = cls.get_dynamo_client()
        client.update_table(
            TableName=cls._table_name,
            ProvisionedThroughput={
                "ReadCapacityUnits": read_capacity,
                "WriteCapacityUnits": write_capacity,
            },
        )

    @staticmethod
    def get_user_conversations(user_id: str) -> list:
        """Récupère toutes les conversations d'un utilisateur en utilisant l'index"""
        dynamo_resource = boto3.resource(
            "dynamodb",
            region_name=env_vars.AWS_REGION_NAME,
            aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY,
        )
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

            dynamo_resource = boto3.resource(
                "dynamodb",
                region_name=env_vars.AWS_REGION_NAME,
                aws_access_key_id=env_vars.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env_vars.AWS_SECRET_ACCESS_KEY,
            )
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
