import logging
import aiohttp
import json
from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from .config import env_vars
from .utils import Utils
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
TELEGRAM_API_URL = "https://api.telegram.org/bot"
TELEGRAM_SEND_MESSAGE_URL = TELEGRAM_API_URL + "{token}/sendMessage"


class TelegramBot:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramBot, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if TelegramBot._initialized:
            return

        TelegramBot._initialized = True

        self.token = env_vars.TELEGRAM_BOT_TOKEN
        self.session = aiohttp.ClientSession()

        # Initialize the bot with minimal configuration
        self.application = Application.builder().token(self.token).concurrent_updates(True).build()
        self._setup_handlers()

        # Initialize the bot instance for direct API calls
        self.bot = self.application.bot

    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        Utils.log_error(f"Unhandled exception: {context.error}")

    def _setup_handlers(self) -> None:
        """Configure les gestionnaires de commandes du bot"""
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("settings", self._settings_command))
        self.application.add_handler(CommandHandler("stats", self._stats_command))
        self.application.add_handler(CommandHandler("clear", self._clear_command))
        self.application.add_handler(CallbackQueryHandler(self._button_click))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère la commande /start"""
        if not update.message or not update.effective_chat:
            return

        welcome_message = (
            "👋 Bonjour! Je suis votre assistant conversationnel.\n\n"
            "Je peux vous aider avec diverses tâches et répondre à vos questions.\n\n"
            "Commandes disponibles:\n"
            "🔹 /help - Afficher l'aide détaillée\n"
            "🔹 /settings - Configurer vos préférences\n"
            "🔹 /stats - Voir vos statistiques\n"
            "🔹 /clear - Effacer l'historique\n\n"
            "Pour commencer, envoyez-moi simplement un message!"
        )
        await update.message.reply_text(welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère la commande /help"""
        if not update.message or not update.effective_chat:
            return

        help_message = (
            "📚 Guide d'utilisation\n\n"
            "1️⃣ Conversation normale:\n"
            "   - Envoyez simplement vos messages\n"
            "   - Je maintiens le contexte de la conversation\n\n"
            "2️⃣ Commandes disponibles:\n"
            "   🔸 /start - Démarrer une nouvelle conversation\n"
            "   🔸 /help - Afficher ce message d'aide\n"
            "   🔸 /settings - Configurer vos préférences\n"
            "   🔸 /stats - Voir vos statistiques\n"
            "   🔸 /clear - Effacer l'historique\n\n"
            "3️⃣ Bonnes pratiques:\n"
            "   - Soyez précis dans vos questions\n"
            "   - Une question à la fois\n"
            "   - Utilisez /clear pour recommencer\n\n"
            "Pour toute question ou problème, n'hésitez pas à demander!"
        )
        await update.message.reply_text(help_message)

    async def _settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère la commande /settings"""
        if not update.message or not update.effective_chat:
            return

        keyboard = [
            [
                InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
                InlineKeyboardButton("🌍 Langue", callback_data="settings_language"),
            ],
            [
                InlineKeyboardButton("📝 Format des réponses", callback_data="settings_format"),
                InlineKeyboardButton("🎨 Thème", callback_data="settings_theme"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚙️ Paramètres\n\n" "Choisissez un paramètre à configurer:", reply_markup=reply_markup
        )

    async def _stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère la commande /stats"""
        if not update.effective_chat or not update.message:
            return

        if not update.message and not update.callback_query:
            Utils.log_info("Ignored update: not a message or callback query.")
            return

        chat_id = str(update.effective_chat.id)
        try:
            # Récupérer les statistiques depuis DynamoDB
            messages = Utils.get_conversation_messages(chat_id)

            total_messages = len(messages)
            if total_messages > 0:
                first_message = min(messages, key=lambda x: x["timestamp"])
                first_date = datetime.fromisoformat(first_message["timestamp"])
                average_messages_per_day = total_messages / max(
                    1, (datetime.now() - first_date).days
                )

                stats_message = (
                    "📊 Vos Statistiques\n\n"
                    f"📝 Nombre total de messages: {total_messages}\n"
                    f"📅 Premier message: {first_date.strftime('%d/%m/%Y')}\n"
                    f"💬 Conversation active depuis: {(datetime.now() - first_date).days} jours\n"
                    f"📈 Moyenne de messages par jour: {average_messages_per_day:.1f}"
                )
            else:
                stats_message = (
                    "📊 Vos Statistiques\n\n"
                    "Vous n'avez pas encore de messages.\n"
                    "Commencez à discuter pour voir vos statistiques!"
                )

            await update.message.reply_text(stats_message)

        except Exception as e:
            Utils.log_error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            await update.message.reply_text(
                "Désolé, une erreur s'est produite lors de la récupération de vos statistiques."
            )

    async def _clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère la commande /clear"""
        if not update.message or not update.effective_chat:
            return

        keyboard = [
            [
                InlineKeyboardButton("✅ Oui, effacer", callback_data="clear_confirm"),
                InlineKeyboardButton("❌ Non, annuler", callback_data="clear_cancel"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🗑️ Êtes-vous sûr de vouloir effacer l'historique de conversation?\n"
            "Cette action est irréversible.",
            reply_markup=reply_markup,
        )

    async def _button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère les clics sur les boutons inline"""
        if not update.callback_query or not update.effective_chat:
            return

        query = update.callback_query
        await query.answer()

        if not query.data:
            return

        if query.data.startswith("settings_"):
            setting = query.data.split("_")[1]
            messages = {
                "notifications": "🔔 Les paramètres de notification seront bientôt disponibles!",
                "language": "🌍 Le support multilingue sera ajouté prochainement!",
                "format": "📝 Les options de format seront disponibles bientôt!",
                "theme": "🎨 La personnalisation du thème arrive bientôt!",
            }
            await query.edit_message_text(
                messages.get(setting, "⚙️ Cette option n'est pas encore disponible.")
            )

        elif query.data.startswith("clear_"):
            action = query.data.split("_")[1]
            chat_id = str(update.effective_chat.id)
            if action == "confirm":
                try:
                    # Supprimer les messages
                    Utils.delete_conversation_messages(chat_id)
                    await query.edit_message_text("🗑️ Historique effacé avec succès!")
                except Exception as e:
                    Utils.log_error(f"Erreur lors de la suppression de l'historique: {str(e)}")
                    await query.edit_message_text(
                        "❌ Une erreur s'est produite lors de la suppression de l'historique."
                    )
            else:
                await query.edit_message_text("❌ Opération annulée.")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère les messages texte reçus"""
        if not update.effective_chat or not update.message:
            return

        if not update.message and not update.callback_query:
            Utils.log_info("Ignored update: not a message or callback query.")
            return

        chat_id = str(update.effective_chat.id)
        message_text = update.message.text

        try:
            Utils.log_info(
                f"Message reçu de Telegram - Chat ID: {chat_id}, Message: {message_text}"
            )

            # Utiliser directement le client Mistral
            from .main import client, model

            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": message_text,
                    },
                ],
            )

            if not chat_response.choices:
                raise ValueError("No response received from Mistral AI")

            # Sauvegarder dans DynamoDB
            timestamp = datetime.now().isoformat()
            response = {
                "id": {
                    "S": f"{chat_response.id}",
                },
                "conversation_id": {"S": chat_id},
                "timestamp": {"S": timestamp},
                "question": {
                    "S": f"{message_text}",
                },
                "answer": {
                    "S": f"{chat_response.choices[0].message.content}",
                },
                "source": {"S": "telegram"},
            }
            Utils.insert_data(response)

            # Envoyer la réponse à l'utilisateur
            await update.message.reply_text(chat_response.choices[0].message.content)

        except Exception as e:
            Utils.log_error(f"Erreur lors du traitement du message Telegram: {str(e)}")
            await update.message.reply_text(
                "Désolé, une erreur s'est produite lors du traitement de votre message."
            )

    async def setup_webhook(self) -> None:
        """Configure le webhook pour le bot"""
        webhook_url = f"{env_vars.TELEGRAM_WEBHOOK_URL}{env_vars.TELEGRAM_WEBHOOK_PATH}"
        await self.application.bot.set_webhook(webhook_url)
        Utils.log_info(f"Webhook set to {webhook_url}")

    async def _send_message(
        self, chat_id: int, text: str, reply_markup: Optional[Dict] = None
    ) -> bool:
        """Send message directly using Telegram Bot API"""
        url = TELEGRAM_SEND_MESSAGE_URL.format(token=self.token)
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            async with self.session.post(url, json=payload) as response:
                result = await response.json()
                if not result.get("ok"):
                    logger.error(f"Failed to send message: {result}")
                    return False
                return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False

    async def handle_update(self, update_data: dict) -> dict:
        """
        Handle updates received via webhook.
        Returns a dictionary with status information.
        """
        try:
            logger.info(f"Received update: {update_data}")

            # Create the update object
            update = Update.de_json(update_data, self.bot)
            if not update or not update.effective_chat:
                logger.error("Failed to create update object from data or no chat")
                return {"statusCode": 400, "body": "Failed to process update"}

            # Process the command
            message = update.message or update.callback_query.message
            if not message:
                return {"statusCode": 400, "body": "No message in update"}

            chat_id = update.effective_chat.id

            # Handle different types of updates
            if update.message and update.message.text:
                text = update.message.text.lower()
                if text.startswith("/start"):
                    welcome_msg = (
                        "👋 Bonjour! Je suis votre assistant conversationnel.\n\n"
                        "Je peux vous aider avec diverses tâches et répondre à vos questions.\n\n"
                        "Commandes disponibles:\n"
                        "🔹 /help - Afficher l'aide détaillée\n"
                        "🔹 /settings - Configurer vos préférences\n"
                        "🔹 /stats - Voir vos statistiques\n"
                        "🔹 /clear - Effacer l'historique\n\n"
                        "Pour commencer, envoyez-moi simplement un message!"
                    )
                    await self._send_message(chat_id, welcome_msg)
                elif text.startswith("/help"):
                    help_msg = (
                        "📚 Guide d'utilisation\n\n"
                        "1️⃣ Conversation normale:\n"
                        "   - Envoyez simplement vos messages\n"
                        "   - Je maintiens le contexte de la conversation\n\n"
                        "2️⃣ Commandes disponibles:\n"
                        "   🔸 /start - Démarrer une nouvelle conversation\n"
                        "   🔸 /help - Afficher ce message d'aide\n"
                        "   🔸 /settings - Configurer vos préférences\n"
                        "   🔸 /stats - Voir vos statistiques\n"
                        "   🔸 /clear - Effacer l'historique\n\n"
                        "3️⃣ Bonnes pratiques:\n"
                        "   - Soyez précis dans vos questions\n"
                        "   - Une question à la fois\n"
                        "   - Utilisez /clear pour recommencer\n\n"
                        "Pour toute question ou problème, n'hésitez pas à demander!"
                    )
                    await self._send_message(chat_id, help_msg)
                else:
                    # Handle regular messages
                    response = (
                        "Je suis un bot simple. Utilisez /help pour voir les commandes disponibles."
                    )
                    await self._send_message(chat_id, response)

            return {"statusCode": 200, "body": "Update processed successfully"}

        except Exception as e:
            error_msg = f"Error processing update: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"statusCode": 500, "body": error_msg}


telegram_bot = TelegramBot()
