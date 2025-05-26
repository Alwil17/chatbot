from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from src.utils import Utils
from pytest import LogCaptureFixture
import pytest


@pytest.mark.asyncio
async def test_insert_and_get_messages(mock_dynamo: Any) -> None:
    """Test l'insertion et la récupération des messages"""
    conversation_id = str(uuid4())

    # Premier message
    message1 = {
        "id": {"S": str(uuid4())},
        "conversation_id": {"S": conversation_id},
        "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
        "question": {"S": "Test question 1"},
        "answer": {"S": "Test answer 1"},
        "source": {"S": "api"},
    }

    await Utils.insert_data(message1)
    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 1
    assert messages[0]["question"]["S"] == "Test question 1"
    assert messages[0]["answer"]["S"] == "Test answer 1"

    # Deuxième message
    message2 = {
        "id": {"S": str(uuid4())},
        "conversation_id": {"S": conversation_id},
        "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
        "question": {"S": "Test question 2"},
        "answer": {"S": "Test answer 2"},
        "source": {"S": "api"},
    }

    await Utils.insert_data(message2)
    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 2

    # Test batch write
    batch_messages = []
    for i in range(3):
        batch_messages.append(
            {
                "id": {"S": str(uuid4())},
                "conversation_id": {"S": conversation_id},
                "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
                "question": {"S": f"Batch question {i}"},
                "answer": {"S": f"Batch answer {i}"},
                "source": {"S": "api"},
            }
        )

    await Utils.batch_write(batch_messages)
    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 5


@pytest.mark.asyncio
async def test_delete_conversation(mock_dynamo: Any) -> None:
    """Test la suppression d'une conversation"""
    conversation_id = str(uuid4())

    # Créer quelques messages
    messages = []
    for i in range(3):
        message = {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "question": {"S": f"Question {i}"},
            "answer": {"S": f"Answer {i}"},
            "source": {"S": "api"},
        }
        messages.append(message)

    await Utils.batch_write(messages)

    # Vérifier que les messages sont bien présents
    stored_messages = await Utils.get_conversation_messages(conversation_id)
    assert len(stored_messages) == 3

    # Supprimer la conversation
    await Utils.delete_conversation_messages(conversation_id)

    # Vérifier que les messages ont été supprimés
    remaining_messages = await Utils.get_conversation_messages(conversation_id)
    assert len(remaining_messages) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_conversation(mock_dynamo: Any) -> None:
    """Test la suppression d'une conversation inexistante"""
    conversation_id = str(uuid4())
    await Utils.delete_conversation_messages(conversation_id)
    messages = await Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_get_user_conversations(mock_dynamo: Any) -> None:
    """Test la récupération des conversations d'un utilisateur"""
    user_id = str(uuid4())
    conversation_id = str(uuid4())

    # Créer quelques messages
    messages = [
        {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "user_id": {"S": user_id},
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "question": {"S": f"Test question {i}"},
            "answer": {"S": f"Test answer {i}"},
            "source": {"S": "api"},
        }
        for i in range(3)
    ]

    for message in messages:
        await Utils.insert_data(message)

    # Récupérer les conversations
    conversations = await Utils.get_user_conversations(user_id)
    assert len(conversations) == 1
    assert conversations[0]["conversation_id"] == conversation_id
    assert conversations[0]["messages_count"] == 3


def test_logging(caplog: LogCaptureFixture) -> None:
    """Test les fonctions de logging"""
    test_message = "Test log message"

    # Capture les logs du logger utilisé par Utils
    caplog.set_level("INFO", logger="uvicorn.error")
    Utils.log_info(test_message)
    assert test_message in caplog.text

    caplog.set_level("ERROR", logger="uvicorn.error")
    Utils.log_error(test_message)
    assert test_message in caplog.text

    caplog.set_level("DEBUG", logger="uvicorn.error")
    Utils.log_debug(test_message)
    assert test_message in caplog.text
