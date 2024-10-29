import os
from pytz import timezone
from datetime import time
from datetime import timedelta
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    JobQueue,
    CallbackQueryHandler,
    ConversationHandler
)
from chatbot.handlers import (
    button_callback,
    start,
    message_handler,
    new_session,
    broadcast_daily,
    SYSTEM_PROMPT_SP,
    CANCEL_SP
)
from chatbot.filters import AuthFilter, MessageFilter
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()


def telegram_bot():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(MessageFilter, message_handler))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.job_queue.run_daily(broadcast_daily, time(hour=7, minute=0, second=0, tzinfo=timezone('Asia/Phnom_Penh')))

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)