import logging
import aiohttp
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
        self._session = None  # Will be initialized when needed

        # Initialize the bot with minimal configuration
        self.application = Application.builder().token(self.token).concurrent_updates(True).build()
        self._setup_handlers()

        # Initialize the bot instance for direct API calls
        self.bot = self.application.bot

    @property
    async def session(self):
        """Lazy initialization of aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

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
        await self.bot.send_message(
            chat_id=update.effective_chat.id, text=welcome_message, parse_mode="HTML"
        )

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
        await self.bot.send_message(
            chat_id=update.effective_chat.id, text=help_message, parse_mode="HTML"
        )

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
        await self.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚙️ Paramètres\n\nChoisissez un paramètre à configurer:",
            reply_markup=reply_markup,
            parse_mode="HTML",
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

            await self.bot.send_message(
                chat_id=update.effective_chat.id, text=stats_message, parse_mode="HTML"
            )

        except Exception as e:
            Utils.log_error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            await self.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Désolé, une erreur s'est produite lors de la récupération des statistiques.",
                parse_mode="HTML",
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
        await self.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🗑️ Êtes-vous sûr de vouloir effacer l'historique de conversation?\n"
            "Cette action est irréversible.",
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    async def _button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère les clics sur les boutons inline"""
        if not update.callback_query or not update.effective_chat:
            return

        query = update.callback_query
        await query.answer()
        chat_id = update.effective_chat.id

        try:
            if query.data == "clear_confirm":
                # Supprimer l'historique de conversation
                Utils.delete_conversation_messages(str(chat_id))
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="✅ L'historique de conversation a été effacé avec succès.",
                    parse_mode="HTML",
                )
                # Delete the original message with buttons
                await query.delete_message()
            elif query.data == "clear_cancel":
                await self.bot.send_message(
                    chat_id=chat_id, text="❌ Opération annulée.", parse_mode="HTML"
                )
                # Delete the original message with buttons
                await query.delete_message()
            elif query.data.startswith("settings_"):
                setting = query.data.split("_")[1]
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚙️ Paramètre sélectionné: {setting}\n"
                    "Cette fonctionnalité est en cours de développement.",
                    parse_mode="HTML",
                )
        except Exception as e:
            logger.error(f"Error in button_click: {str(e)}")
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Une erreur s'est produite lors du traitement de votre demande.",
                parse_mode="HTML",
            )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gère les messages entrants"""
        if not update.message or not update.effective_chat or not update.message.text:
            return

        chat_id = update.effective_chat.id

        try:
            # Enregistrer le message de l'utilisateur dans DynamoDB
            message_data = {
                "chat_id": {"S": str(chat_id)},
                "message_id": {"S": str(update.message.message_id)},
                "user_id": {"S": str(update.message.from_user.id)},
                "username": {"S": update.message.from_user.username or "unknown"},
                "message": {"S": update.message.text},
                "role": {"S": "user"},
                "timestamp": {"S": datetime.now().isoformat()},
                "source": {"S": "telegram"},
            }
            Utils.insert_data(message_data)

            # Simuler une réponse du chatbot
            chat_response = (
                "Je suis un chatbot basique. Cette fonctionnalité est en cours de développement."
            )

            # Enregistrer la réponse dans DynamoDB
            response = {
                "chat_id": {"S": str(chat_id)},
                "message_id": {"S": f"bot_{int(datetime.now().timestamp())}"},
                "user_id": {"S": str(self.application.bot.id)},
                "username": {"S": self.application.bot.username or "bot"},
                "message": {"S": chat_response},
                "role": {"S": "assistant"},
                "timestamp": {"S": datetime.now().isoformat()},
                "source": {"S": "telegram"},
            }
            Utils.insert_data(response)

            # Envoyer la réponse à l'utilisateur
            await self.bot.send_message(chat_id=chat_id, text=chat_response, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Error in _handle_message: {str(e)}")
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Désolé, une erreur s'est produite lors du traitement de votre message.",
                    parse_mode="HTML",
                )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {str(send_error)}")

    async def setup_webhook(self) -> None:
        """Configure le webhook pour le bot"""
        webhook_url = f"{env_vars.TELEGRAM_WEBHOOK_URL}{env_vars.TELEGRAM_WEBHOOK_PATH}"
        await self.application.bot.set_webhook(webhook_url)
        Utils.log_info(f"Webhook set to {webhook_url}")

    # In your TelegramBot class, update the _send_message method:
    async def _send_message(self, chat_id: int, text: str) -> bool:
        """Send a message using the Telegram Bot API directly"""
        if not text:
            logger.warning("Attempted to send empty message")
            return False

        try:
            # Use the bot's send_message method directly
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False

    async def close(self):
        """Close the aiohttp session when done"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def handle_update(self, update_data: dict) -> dict:
        """Handle incoming Telegram update"""
        try:
            update = Update.de_json(update_data, self.bot)
            if not update or not update.effective_chat:
                logger.error("Invalid update or no chat information")
                return {"statusCode": 400, "body": "Invalid update"}

            chat_id = update.effective_chat.id
            message_text = update.message.text if update.message else ""

            if message_text.startswith("/start"):
                welcome_msg = "👋 Bonjour! Je suis votre assistant conversationnel."
                await self._send_message(chat_id, welcome_msg)
            elif message_text.startswith("/help"):
                help_msg = "📚 Guide d'utilisation\n\n1️⃣ Conversation normale:\n..."
                await self._send_message(chat_id, help_msg)
            else:
                response = (
                    "Je suis un bot simple. Utilisez /help pour voir les commandes disponibles."
                )
                await self._send_message(chat_id, response)

            return {"statusCode": 200, "body": "Update processed"}

        except Exception as e:
            logger.error(f"Error processing update: {str(e)}")
            return {"statusCode": 500, "body": "Internal server error"}


telegram_bot = TelegramBot()
