import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from mistralai import Chat


def test_root(client):
    """Test l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_rate_limit():
    """Test le rate limiting"""
    client1 = TestClient(app)
    for _ in range(4):
        response = client1.get("/")
        assert response.status_code == 200
    # La 6ème requête devrait être limitée
    response = client1.get("/")
    assert response.status_code == 429
    del client1


@pytest.mark.asyncio
async def test_chat_endpoint(client, mock_dynamo):
    """Test l'endpoint de chat"""
    mock_response = MagicMock()
    mock_response.id = "test-id"
    mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]

    with patch.object(Chat, "complete", return_value=mock_response):
        response = client.get("/chat?question=Test question")
        assert response.status_code == 200
        data = response.json()
        assert data["question"]["S"] == "Test question"
        assert data["answer"]["S"] == "Test response"
        assert "conversation_id" in data
        assert "timestamp" in data


def test_get_conversation(client, sample_conversation, mock_dynamo):
    """Test la récupération des messages d'une conversation"""
    conversation_id, expected_messages = sample_conversation

    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200

    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 2

    # Vérifier que les messages sont dans le bon ordre
    messages = data["messages"]
    assert messages[0]["question"] == "Test question 1"
    assert messages[1]["question"] == "Test question 2"


def test_get_nonexistent_conversation(client, mock_dynamo):
    """Test la récupération d'une conversation inexistante"""
    response = client.get("/conversations/nonexistent-id")
    assert response.status_code == 200
    assert response.json() == {"messages": []}


@pytest.mark.asyncio
async def test_telegram_webhook(client, mock_dynamo):
    """Test l'endpoint webhook Telegram"""
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {"id": 123456789, "first_name": "Test", "username": "test_user"},
            "chat": {"id": 123456789, "type": "private"},
            "text": "Test message",
        },
    }

    with patch("src.telegram_bot.telegram_bot.handle_update") as mock_handle_update:
        response = client.post("/telegram/webhook", json=test_update)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_handle_update.assert_called_once()
