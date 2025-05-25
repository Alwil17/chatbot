from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .config import env_vars
from .utils import Utils
import json
from uuid import uuid4

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(env_vars.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Configure les gestionnaires de commandes du bot"""
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la commande /start"""
        await update.message.reply_text(
            "Bonjour! Je suis votre assistant. Comment puis-je vous aider aujourd'hui?"
        )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les messages texte reçus"""
        chat_id = str(update.effective_chat.id)  # Convertir en string pour l'utiliser comme conversation_id
        user_id = update.effective_user.id
        message_text = update.message.text
        
        try:
            # Appel à l'API Mistral via les fonctions existantes
            from .main import chat
            Utils.log_info(f"Message reçu de Telegram - Chat ID: {chat_id}, Message: {message_text}")
            
            # Utiliser le chat_id de Telegram comme conversation_id
            response = await chat(message_text, conversation_id=chat_id)
            
            # Envoyer la réponse à l'utilisateur
            await update.message.reply_text(response["answer"]["S"])
            
        except Exception as e:
            Utils.log_error(f"Erreur lors du traitement du message Telegram: {str(e)}")
            await update.message.reply_text(
                "Désolé, une erreur s'est produite lors du traitement de votre message."
            )

    async def setup_webhook(self):
        """Configure le webhook pour le bot"""
        webhook_url = f"{env_vars.TELEGRAM_WEBHOOK_URL}{env_vars.TELEGRAM_WEBHOOK_PATH}"
        await self.application.bot.set_webhook(webhook_url)
        Utils.log_info(f"Webhook set to {webhook_url}")

    async def handle_update(self, update_data: dict):
        """Gère les mises à jour reçues via webhook"""
        async with self.application:
            await self.application.process_update(
                Update.de_json(data=update_data, bot=self.application.bot)
            )

telegram_bot = TelegramBot() 