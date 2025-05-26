from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mangum import Mangum
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Optional, Any, AsyncGenerator, Union, Awaitable, Callable
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import env_vars
from .utils import Utils
from .telegram_bot import telegram_bot
from .handlers import generate_response

# Création du limiteur de taux
limiter = Limiter(key_func=get_remote_address)

# Type pour le handler d'exception
ExceptionHandler = Union[
    Callable[[Request, Exception], Union[Response, Awaitable[Response]]],
    Callable[[WebSocket, Exception], Awaitable[None]],
]


@asynccontextmanager
async def app_lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    Utils.log_info("Starting the application")
    await telegram_bot.setup_webhook()
    yield


app = FastAPI(
    title="ChatBot API",
    description="Chatbot API description",
    version="1.0.0",
    lifespan=app_lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request) -> Dict[str, str]:
    return {"msg": "Hello World"}


@app.post(env_vars.TELEGRAM_WEBHOOK_PATH)
@limiter.limit("60/minute")
async def telegram_webhook(request: Request) -> Dict[str, str]:
    """Endpoint pour recevoir les mises à jour de Telegram"""
    update_data = await request.json()
    await telegram_bot.handle_update(update_data)
    return {"status": "ok"}


@app.get("/chat")
@limiter.limit("30/minute")
async def handle_chat_request(
    request: Request, question: str, conversation_id: Optional[str] = None
) -> Dict[str, Dict[str, str]]:
    Utils.log_info(f"Nouvelle question reçue: {question}")

    if not conversation_id:
        conversation_id = str(uuid4())
        Utils.log_info(f"Nouvelle conversation créée avec ID: {conversation_id}")

    try:
        response = await generate_response(question)

        timestamp = datetime.now(timezone.utc).isoformat()
        response_item = {
            "id": {"S": str(uuid4())},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": timestamp},
            "question": {"S": question},
            "answer": {"S": response},
            "source": {"S": "api"},
        }
        await Utils.insert_data(response_item)
        Utils.log_info("Traitement de la question terminé avec succès")
        return response_item
    except Exception as e:
        Utils.log_error(f"Erreur lors du traitement de la question: {str(e)}")
        raise e


@app.get("/conversations/{conversation_id}")
@limiter.limit("30/minute")
async def get_conversation(
    request: Request, conversation_id: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Récupère tous les messages d'une conversation"""
    messages = await Utils.get_conversation_messages(conversation_id)
    return {"messages": messages}


@app.get("/chats/{user_id}")
@limiter.limit("30/minute")
async def get_user_chats(request: Request, user_id: str) -> Dict[str, Any]:
    """Récupère toutes les conversations d'un utilisateur"""
    messages = await Utils.get_user_conversations(user_id)
    return {"conversations": messages}


async def get_conversation_history(conversation_id: str) -> Dict[str, Any]:
    """
    Récupère l'historique d'une conversation.
    """
    try:
        messages = await Utils.get_conversation_messages(conversation_id)
        return {
            "messages": messages,
            "total": len(messages),
        }
    except Exception as e:
        Utils.log_error(f"Erreur lors de la récupération de l'historique: {str(e)}")
        raise e


async def get_user_conversations(user_id: str) -> Dict[str, Any]:
    """
    Récupère toutes les conversations d'un utilisateur.
    """
    try:
        conversations = await Utils.get_user_conversations(user_id)
        return {
            "conversations": conversations,
            "total": len(conversations),
        }
    except Exception as e:
        Utils.log_error(f"Erreur lors de la récupération des conversations: {str(e)}")
        raise e


handler = Mangum(app)
