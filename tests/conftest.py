import pytest
from fastapi.testclient import TestClient
import boto3
from moto import mock_dynamodb
from datetime import datetime
from uuid import uuid4

from src.main import app
from src.config import env_vars
from src.utils import Utils

@pytest.fixture
def test_app():
    """Fixture pour l'application FastAPI"""
    return app

@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI"""
    return TestClient(app)

@pytest.fixture
def mock_dynamo():
    """Fixture pour mocker DynamoDB"""
    with mock_dynamodb():
        # Créer une table de test
        dynamo = boto3.resource('dynamodb', region_name='eu-west-3')
        
        # Créer la table avec les mêmes attributs que la production
        table = dynamo.create_table(
            TableName=env_vars.DYNAMO_TABLE,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
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
        
        yield table

@pytest.fixture
def sample_conversation(mock_dynamo):
    """Fixture pour créer des données de test"""
    conversation_id = str(uuid4())
    messages = [
        {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": datetime.utcnow().isoformat()},
            "question": {"S": "Test question 1"},
            "answer": {"S": "Test answer 1"},
            "source": {"S": "api"}
        },
        {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": datetime.utcnow().isoformat()},
            "question": {"S": "Test question 2"},
            "answer": {"S": "Test answer 2"},
            "source": {"S": "api"}
        }
    ]
    
    for message in messages:
        Utils.insert_data(message)
    
    return conversation_id, messages 