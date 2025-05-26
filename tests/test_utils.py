from datetime import datetime, timezone
from uuid import uuid4
from src.utils import Utils


def test_insert_and_get_conversation_messages(mock_dynamo):
    """Test l'insertion et la récupération des messages"""
    conversation_id = str(uuid4())
    message = {
        "id": {"S": str(uuid4())},
        "conversation_id": {"S": conversation_id},
        "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
        "question": {"S": "Test question"},
        "answer": {"S": "Test answer"},
        "source": {"S": "api"},
    }

    # Test insertion
    assert Utils.insert_data(message) == True

    # Test récupération
    messages = Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 1
    assert messages[0]["question"] == "Test question"
    assert messages[0]["answer"] == "Test answer"


def test_delete_conversation_messages(mock_dynamo, sample_conversation):
    """Test la suppression des messages d'une conversation"""
    conversation_id, _ = sample_conversation

    # Vérifier que les messages existent
    messages = Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 2

    # Supprimer les messages
    assert Utils.delete_conversation_messages(conversation_id) == True

    # Vérifier que les messages ont été supprimés
    messages = Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 0


def test_delete_nonexistent_conversation(mock_dynamo):
    """Test la suppression d'une conversation inexistante"""
    conversation_id = str(uuid4())
    assert Utils.delete_conversation_messages(conversation_id) == True
    messages = Utils.get_conversation_messages(conversation_id)
    assert len(messages) == 0


def test_get_user_conversations(mock_dynamo):
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
        Utils.insert_data(message)

    # Récupérer les conversations
    conversations = Utils.get_user_conversations(user_id)
    assert len(conversations) == 1
    assert conversations[0]["conversation_id"] == conversation_id
    assert conversations[0]["messages_count"] == 3


def test_logging(caplog):
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
