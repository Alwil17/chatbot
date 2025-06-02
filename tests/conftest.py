import pytest
import asyncio
from fastapi.testclient import TestClient
import boto3
from moto import mock_aws
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI
from mypy_boto3_dynamodb.service_resource import Table

from src.main import app
from src.config import env_vars
from src.utils import Utils

# Create a new event loop for the test session
event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)


@pytest.fixture(autouse=True)
def aws_credentials() -> None:
    """Fixture pour les credentials AWS de test"""
    import os

    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-3"
    os.environ["AWS_REGION"] = "eu-west-3"
    os.environ.pop("AWS_PROFILE", None)


@pytest.fixture(autouse=True)
def mock_aws_services():
    """Fixture pour mocker tous les services AWS"""
    with mock_aws():
        yield


@pytest.fixture
def test_app() -> FastAPI:
    """Fixture pour l'application FastAPI"""
    return app


@pytest.fixture
def client() -> TestClient:
    """Fixture pour le client de test FastAPI"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def ensure_cleanup():
    """Ensure cleanup after tests"""
    from src.telegram_bot import telegram_bot

    # Setup code before test
    yield  # Test runs here

    # Teardown code after test
    import asyncio

    # Close the aiohttp session if it exists
    if hasattr(telegram_bot, "_session") and telegram_bot._session is not None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(telegram_bot.close())


@pytest.fixture
def mock_dynamo(aws_credentials: None) -> Table:
    """Fixture pour mocker DynamoDB"""
    # Créer une table de test
    dynamo = boto3.resource("dynamodb", region_name="eu-west-3")

    # Créer la table avec les mêmes attributs que la production
    table: Table = dynamo.create_table(
        TableName=env_vars.DYNAMO_TABLE,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "conversation_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "conversation_id-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "conversation_id", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            },
            {
                "IndexName": "user_id-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "user_id", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    return table


@pytest.fixture
def sample_conversation(mock_dynamo: Table) -> tuple[str, list[dict[str, dict[str, str]]]]:
    """Fixture pour créer des données de test"""
    conversation_id = str(uuid4())
    user_id = str(uuid4())  # Generate a user ID
    messages = [
        {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "user_id": {"S": user_id},  # Add user_id
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "question": {"S": "Test question 1"},
            "answer": {"S": "Test answer 1"},
            "source": {"S": "api"},
        },
        {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "user_id": {"S": user_id},  # Add user_id
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "question": {"S": "Test question 2"},
            "answer": {"S": "Test answer 2"},
            "source": {"S": "api"},
        },
    ]

    for message in messages:
        Utils.insert_data(message)

    return conversation_id, messages
