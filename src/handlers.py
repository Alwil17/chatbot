from telegram import Update
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any
from .utils import Utils
from mistralai import Mistral
from .config import env_vars

api_key = env_vars.MISTRAL_API_KEY
model = "mistral-small-latest"
client = Mistral(api_key=api_key)


async def generate_response(message: str) -> str:
    """Génère une réponse en utilisant l'API Mistral"""
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": message,
            },
        ],
    )

    if not chat_response.choices:
        raise ValueError("No response received from Mistral AI")

    return chat_response.choices[0].message.content


async def handle_telegram_message(
    update: Update, message: str, conversation_id: str
) -> Dict[str, Any]:
    """
    Gère une conversation avec l'utilisateur via Telegram.
    """
    try:
        # Enregistrer la question
        question_id = str(uuid4())
        question_item = {
            "id": {"S": question_id},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "question": {"S": message},
            "source": {"S": "telegram"},
        }
        await Utils.insert_data(question_item)

        # Générer la réponse avec Mistral
        response = await generate_response(message)

        # Enregistrer la réponse
        answer_id = str(uuid4())
        answer_item = {
            "id": {"S": answer_id},
            "conversation_id": {"S": conversation_id},
            "timestamp": {"S": datetime.now(timezone.utc).isoformat()},
            "answer": {"S": response},
            "source": {"S": "mistral"},
        }
        await Utils.insert_data(answer_item)

        return answer_item

    except Exception as e:
        Utils.log_error(f"Erreur lors du traitement du message: {str(e)}")
        raise e
