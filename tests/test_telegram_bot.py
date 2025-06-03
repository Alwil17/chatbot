import pytest
from unittest.mock import patch, MagicMock
from src.telegram_bot import TelegramBot
from telegram import Update, Message, Chat, User
from telegram.constants import ChatType


@pytest.fixture
def mock_update():
    """Fixture for creating a mock Telegram update"""

    def create_update(text: str):
        chat = Chat(
            id=12345,
            type=ChatType.PRIVATE,
            first_name="Test",
            last_name="User",
            username="testuser",
        )
        user = User(
            id=12345, first_name="Test", last_name="User", username="testuser", is_bot=False
        )
        message = Message(message_id=1, date=None, chat=chat, from_user=user, text=text)
        return Update(update_id=1, message=message)

    # Return a function that creates a new update with the given text
    return create_update


@pytest.fixture
def mock_context():
    """Fixture for creating a mock context"""
    context = MagicMock()
    context.bot = MagicMock()
    return context


@pytest.mark.asyncio
async def test_handle_update_invalid_update():
    """Test handling an invalid update"""
    bot = TelegramBot()

    # Mock the logger to avoid actual logging during test
    with (
        patch("src.telegram_bot.logger") as mock_logger,
        patch("src.telegram_bot.Update.de_json") as mock_de_json,
    ):
        # Make de_json return None to simulate invalid update
        mock_de_json.return_value = None

        # Call handle_update with invalid data
        result = await bot.handle_update({})

        # Verify the result
        assert result["statusCode"] == 400
        assert result["body"] == "Invalid update"
        # Verify error was logged
        mock_logger.error.assert_called_with("Invalid update or no chat information")
