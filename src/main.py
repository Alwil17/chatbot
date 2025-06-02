from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mangum import Mangum
from mistralai import Mistral
from mistralai import ChatCompletionResponse
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Optional, Any, AsyncGenerator, Union, Awaitable, Callable
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import env_vars
from .utils import Utils
from .telegram_bot import telegram_bot

api_key = env_vars.MISTRAL_API_KEY
model = "mistral-small-latest"
client = Mistral(api_key=api_key)

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
    # Ne pas configurer le webhook au démarrage car l'URL n'est pas encore disponible
    # await telegram_bot.setup_webhook()
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
    try:
        update_data = await request.json()
        if not update_data:
            raise ValueError("Empty update data received")

        # Process the update and get the response
        result = await telegram_bot.handle_update(update_data)

        # Return the appropriate response based on the result
        if result.get("statusCode") == 200:
            return {"status": "ok"}
        else:
            error_msg = result.get("body", "Unknown error")
            Utils.log_error(f"Error in telegram_webhook: {error_msg}")
            return {"status": "error", "message": error_msg}

    except Exception as e:
        error_msg = str(e)
        Utils.log_error(f"Error in telegram_webhook: {error_msg}")
        return {"status": "error", "message": error_msg}


@app.get("/chat")
@limiter.limit("30/minute")
async def chat(
    request: Request, question: str, conversation_id: Optional[str] = None
) -> Dict[str, Dict[str, str]]:
    Utils.log_info(f"Nouvelle question reçue: {question}")

    if not conversation_id:
        conversation_id = str(uuid4())
        Utils.log_info(f"Nouvelle conversation créée avec ID: {conversation_id}")

    try:
        chat_response: ChatCompletionResponse = client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )
        Utils.log_info("Réponse reçue de Mistral AI")

        if not chat_response.choices:
            raise ValueError("No response received from Mistral AI")

        timestamp = datetime.now(timezone.utc).isoformat()
        response = {
            "id": {
                "S": f"{chat_response.id}",
            },
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": timestamp},
            "question": {
                "S": f"{question}",
            },
            "answer": {
                "S": f"{chat_response.choices[0].message.content}",
            },
            "source": {"S": "api"},
        }
        Utils.insert_data(response)
        Utils.log_info("Traitement de la question terminé avec succès")
        return response
    except Exception as e:
        Utils.log_error(f"Erreur lors du traitement de la question: {str(e)}")
        raise e


@app.get("/conversations/{conversation_id}")
@limiter.limit("30/minute")
async def get_conversation(
    request: Request, conversation_id: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Récupère tous les messages d'une conversation"""
    messages = Utils.get_conversation_messages(conversation_id)
    return {"messages": messages}


@app.get("/chats/{user_id}")
@limiter.limit("30/minute")
async def get_user_chats(request: Request, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Récupère toutes les conversations d'un utilisateur"""
    messages = Utils.get_user_conversations(user_id)
    return {"conversations": messages}


handler = Mangum(app)
