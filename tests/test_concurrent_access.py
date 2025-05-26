import pytest
import asyncio
from datetime import datetime, timezone
from uuid import uuid4
from typing import List, Dict, Any

from src.utils import Utils


@pytest.mark.asyncio
async def test_concurrent_writes(mock_dynamo: Any) -> None:
    """Test les écritures concurrentes dans DynamoDB"""
    conversation_id = str(uuid4())
    num_messages = 10

    async def write_message(index: int) -> None:
        message = {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "question": {"S": f"Test question {index}"},
            "answer": {"S": f"Test answer {index}"},
            "source": {"S": "api"},
        }
        await Utils.insert_data(message)

    # Exécuter les écritures en parallèle
    tasks = [write_message(i) for i in range(num_messages)]
    await asyncio.gather(*tasks)

    # Vérifier que tous les messages ont été écrits
    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == num_messages


@pytest.mark.asyncio
async def test_concurrent_reads(mock_dynamo: Any) -> None:
    """Test les lectures concurrentes depuis DynamoDB"""
    conversation_id = str(uuid4())
    num_readers = 5
    results: List[int] = []

    # Créer des données de test
    message = {
        "id": {"S": str(uuid4())},
        "conversation_id": {"S": conversation_id},
        "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
        "question": {"S": "Test question"},
        "answer": {"S": "Test answer"},
        "source": {"S": "api"},
    }
    await Utils.insert_data(message)

    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 1

    async def read_messages() -> None:
        messages = await Utils.get_conversation_messages(conversation_id)
        results.append(len(messages))

    # Exécuter les lectures en parallèle
    tasks = [read_messages() for _ in range(num_readers)]
    await asyncio.gather(*tasks)

    # Vérifier que toutes les lectures ont retourné le même nombre de messages
    assert all(count == results[0] for count in results)


@pytest.mark.asyncio
async def test_concurrent_read_writes(mock_dynamo: Any) -> None:
    """Test les lectures et écritures simultanées"""
    conversation_id = str(uuid4())
    num_operations = 5

    async def write_and_read(index: int) -> None:
        # Écrire un message
        message = {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "question": {"S": f"Test question {index}"},
            "answer": {"S": f"Test answer {index}"},
            "source": {"S": "api"},
        }
        await Utils.insert_data(message)

        # Lire immédiatement après l'écriture
        messages = await Utils.get_conversation_messages(conversation_id)
        # Le nombre de messages devrait être au moins index + 1
        assert len(messages) >= index + 1

    # Exécuter les opérations en parallèle
    tasks = [write_and_read(i) for i in range(num_operations)]
    await asyncio.gather(*tasks)

    # Vérifier le nombre final de messages
    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == num_operations


@pytest.mark.asyncio
async def test_conditional_writes(mock_dynamo: Any) -> None:
    """Test les écritures conditionnelles pour éviter les conflits"""
    conversation_id = str(uuid4())
    message_id = str(uuid4())

    # Premier message
    message1 = {
        "id": {"S": message_id},
        "conversation_id": {"S": conversation_id},
        "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
        "question": {"S": "Original question"},
        "answer": {"S": "Original answer"},
        "source": {"S": "api"},
        "version": {"N": "1"},
    }

    # Deuxième message (mise à jour)
    message2 = {
        "id": {"S": message_id},
        "conversation_id": {"S": conversation_id},
        "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
        "question": {"S": "Updated question"},
        "answer": {"S": "Updated answer"},
        "source": {"S": "api"},
        "version": {"N": "2"},
    }

    async def conditional_write(message: Dict[str, Dict[str, str]], expected_version: int) -> bool:
        try:
            dynamo_client = Utils.get_dynamo_client()
            dynamo_client.put_item(
                TableName=Utils._table_name,  # Utilisation de l'attribut de classe
                Item=message,
                ConditionExpression=(
                    "attribute_not_exists(version) OR version.N = :expected_version"
                ),
                ExpressionAttributeValues={":expected_version": {"N": str(expected_version)}},
            )
            return True
        except dynamo_client.exceptions.ConditionalCheckFailedException:
            return False

    # Écrire le premier message
    assert await conditional_write(message1, 0)

    # Tenter d'écrire le deuxième message avec une version incorrecte
    assert not await conditional_write(message2, 1)

    # Vérifier que le message original est toujours là
    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 1
    assert messages[0]["question"]["S"] == "Original question"
