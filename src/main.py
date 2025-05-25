from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mangum import Mangum
import json, boto3
from mistralai import Mistral
from datetime import datetime
from uuid import uuid4

from .config import env_vars
from .utils import Utils
from .telegram_bot import telegram_bot

api_key = env_vars.MISTRAL_API_KEY
model = "mistral-small-latest"
client = Mistral(api_key=api_key)

@asynccontextmanager
async def app_lifespan(application: FastAPI):
    Utils.log_info("Starting the application")
    await telegram_bot.setup_webhook()
    yield

app = FastAPI(
    title="ChatBot API",
    description="Chatbot API description",
    version="1.0.0",
    lifespan=app_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"msg": "Hello World"}

@app.post(env_vars.TELEGRAM_WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Endpoint pour recevoir les mises à jour de Telegram"""
    update_data = await request.json()
    await telegram_bot.handle_update(update_data)
    return {"status": "ok"}

@app.get("/chat")
async def chat(question: str, conversation_id: str = None):
    Utils.log_info(f"Nouvelle question reçue: {question}")
    
    if not conversation_id:
        conversation_id = str(uuid4())
        Utils.log_info(f"Nouvelle conversation créée avec ID: {conversation_id}")

    try:
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": question,
                },
            ]
        )
        Utils.log_info("Réponse reçue de Mistral AI")
        
        timestamp = datetime.utcnow().isoformat()
        response = {
            "id": {
                "S": f"{chat_response.id}",
            },
            "conversation_id": {
                "S": conversation_id
            },
            "timestamp": {
                "S": timestamp
            },
            "question": {
                "S": f"{question}",
            },
            "answer": {
                "S": f"{chat_response.choices[0].message.content}",
            },
            "source": {
                "S": "api"
            }
        }
        Utils.insert_data(response)
        Utils.log_info("Traitement de la question terminé avec succès")
        return response
    except Exception as e:
        Utils.log_error(f"Erreur lors du traitement de la question: {str(e)}")
        raise e

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Récupère tous les messages d'une conversation"""
    messages = Utils.get_conversation_messages(conversation_id)
    return {"messages": messages}

@app.get("/chats/{user_id}")
async def get_user_chats(user_id: str):
    """Récupère toutes les conversations d'un utilisateur"""
    messages = Utils.get_user_conversations(user_id)
    return {"conversations": messages}

@app.delete("/clear-data")
async def clear_data():
    """Supprime toutes les données de la table"""
    return Utils.clear_table()

handler = Mangum(app)
