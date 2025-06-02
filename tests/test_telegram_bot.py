import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.telegram_bot import TelegramBot, telegram_bot
from telegram import Update, Message, Chat, User
from telegram.constants import ChatType
import json


@pytest.fixture
def mock_update():
    """Fixture for creating a mock Telegram update"""
    def create_update(text: str):
        chat = Chat(
            id=12345,
            type=ChatType.PRIVATE,
            first_name="Test",
            last_name="User",
            username="testuser"
        )
        user = User(
            id=12345,
            first_name="Test",
            last_name="User",
            username="testuser",
            is_bot=False
        )
        message = Message(
            message_id=1,
            date=None,
            chat=chat,
            from_user=user,
            text=text
        )
        return Update(
            update_id=1,
            message=message
        )
    
    # Return a function that creates a new update with the given text
    return create_update


@pytest.fixture
def mock_context():
    """Fixture for creating a mock context"""
    context = MagicMock()
    context.bot = MagicMock()
    return context

@pytest.mark.skip(reason="Skipping this test for now")
@pytest.mark.asyncio
async def test_send_message():
    """Test sending a message using the Telegram API"""
    bot = TelegramBot()
    
    # Create a mock response
    mock_response = AsyncMock()
    mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
    
    # Mock the session's post method to return our mock response
    mock_post = AsyncMock(return_value=mock_response)
    
    # Mock the session context manager
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value.post = mock_post
    
    # Patch the ClientSession to return our mock session
    with patch('aiohttp.ClientSession', return_value=mock_session):
        # Send a test message
        result = await bot._send_message(12345, "Test message")
        
        # Verify the result
        assert result is True
        mock_post.assert_called_once()
        
        # Verify the URL and payload
        args, kwargs = mock_post.call_args
        assert 'https://api.telegram.org/bot' in args[0]  # Check URL contains the base
        assert 'sendMessage' in args[0]
        assert kwargs['json'] == {
            'chat_id': 12345,
            'text': 'Test message',
            'parse_mode': 'HTML'
        }

@pytest.mark.skip(reason="Skipping this test for now")
@pytest.mark.asyncio
async def test_handle_update_start_command(mock_update, mock_context):
    """Test handling a start command update"""
    bot = TelegramBot()
    update = mock_update("/start")  # Create a new update with /start command
    
    # Mock the _send_message method and aiohttp session
    with patch.object(bot, '_send_message', return_value=True) as mock_send, \
         patch('aiohttp.ClientSession') as mock_session:
        
        # Set up mock session
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json.return_value = {"ok": True}
        
        # Call handle_update with a start command
        update_data = update.to_dict()
        result = await bot.handle_update(update_data)
        
        # Verify the result
        assert result["statusCode"] == 200
        assert mock_send.called  # Check that _send_message was called
        
        # Get the actual message text that was sent
        sent_message = mock_send.call_args[0][1]
        assert "Bonjour" in sent_message  # Check welcome message

@pytest.mark.skip(reason="Skipping this test for now")
@pytest.mark.asyncio
async def test_handle_update_help_command(mock_update, mock_context):
    """Test handling a help command update"""
    bot = TelegramBot()
    update = mock_update("/help")  # Create a new update with /help command
    
    # Mock the _send_message method and aiohttp session
    with patch.object(bot, '_send_message', return_value=True) as mock_send, \
         patch('aiohttp.ClientSession') as mock_session:
        
        # Set up mock session
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json.return_value = {"ok": True}
        
        # Call handle_update with a help command
        update_data = update.to_dict()
        result = await bot.handle_update(update_data)
        
        # Verify the result
        assert result["statusCode"] == 200
        assert mock_send.called  # Check that _send_message was called
        
        # Get the actual message text that was sent
        sent_message = mock_send.call_args[0][1]
        assert "Guide d'utilisation" in sent_message  # Check help message

@pytest.mark.skip(reason="Skipping this test for now")
@pytest.mark.asyncio
async def test_handle_update_regular_message(mock_update, mock_context):
    """Test handling a regular message update"""
    bot = TelegramBot()
    update = mock_update("Hello, bot!")  # Create a new update with a regular message
    
    # Mock the _send_message method and aiohttp session
    with patch.object(bot, '_send_message', return_value=True) as mock_send, \
         patch('aiohttp.ClientSession') as mock_session:
        
        # Set up mock session
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json.return_value = {"ok": True}
        
        # Call handle_update with a regular message
        update_data = update.to_dict()
        result = await bot.handle_update(update_data)
        
        # Verify the result
        assert result["statusCode"] == 200
        assert mock_send.called  # Check that _send_message was called
        
        # Get the actual message text that was sent
        sent_message = mock_send.call_args[0][1]
        assert "Je suis un bot simple" in sent_message  # Check default response


@pytest.mark.asyncio
async def test_handle_update_invalid_update():
    """Test handling an invalid update"""
    bot = TelegramBot()
    
    # Mock the logger to avoid actual logging during test
    with patch('src.telegram_bot.logger') as mock_logger, \
         patch('src.telegram_bot.Update.de_json') as mock_de_json:
        
        # Make de_json return None to simulate invalid update
        mock_de_json.return_value = None
        
        # Call handle_update with invalid data
        result = await bot.handle_update({})
        
        # Verify the result
        assert result["statusCode"] == 400
        assert "Failed to process update" in result["body"]
        # Verify error was logged
        mock_logger.error.assert_called()
