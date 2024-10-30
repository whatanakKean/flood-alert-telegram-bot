from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ApplicationBuilder,
    ConversationHandler,
)
from telegram.error import NetworkError, BadRequest
from telegram.constants import ChatAction, ParseMode
from chatbot.html_format import format_message
from chatbot.huggingchat import chatbot, generate_response
from chatbot.queries import fetch_measurement, fetch_metadata, predict_water_level
from chatbot.user import UserManager

# Bot Configuration
SYSTEM_PROMPT_SP = 1
CANCEL_SP = 2
DEFAULT_MODEL_INDEX = 0
FIXED_SYSTEM_PROMPT = f"""
    You are a chatbot called Flood Alert, and your response will only be about Flood and Hydrometeorological Monitoring.

    If the prompt is related to real data that is not given, just say you don't know and refer them to this site https://floodalert.live/
"""
context_data = None


# Initialize UserManager
user_manager = UserManager()


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with buttons when the command /start is issued.""" 
    user = update.effective_user
    user_manager.save_user(user.id, user.first_name, user.username, update.effective_chat.id)
    
    # Define buttons
    keyboard = [
        [InlineKeyboardButton("Start a new chat session", callback_data='new_session')],
        [InlineKeyboardButton("Fetch latest image of the location", callback_data='image')],
        [InlineKeyboardButton("Subscribe to daily flood alerts", callback_data='subscribe')],
        [InlineKeyboardButton("Unsubscribe from daily flood alerts", callback_data='unsubscribe')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with buttons
    await update.message.reply_html(
        f"""<b>🌧️ Greetings, {user.mention_html()}!</b>\n\n
Welcome to <i>Flood Alert</i>! Your go-to source for hydrometeorological updates.\n

💬 How can I assist you today?


🌐 Visit us at: <a href="https://floodalert.live/">floodalert.live</a>\n""",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks.""" 
    query = update.callback_query
    await query.answer()

    if query.data == 'new_session':
        await new_session(query, context)
    elif query.data == 'image':
        await image_station_selection(query)
    elif query.data.startswith("station_"):
        location = query.data[len("station_"):]
        await send_location_image(query, context, location)
    elif query.data == 'subscribe':
        await subscription_station_selection(query)  # Send a new message for subscription
    elif query.data == 'unsubscribe':
        await subscription_station_selection(query, is_unsubscribe=True)
    elif query.data.startswith("location_"):
        location = query.data[len("location_"):]
        await manage_subscription(query, context, location)

async def image_station_selection(query, is_unsubscribe: bool = False) -> None:
    """Prompt the user to select a station for subscription or unsubscription.""" 
    keyboard = [[InlineKeyboardButton(station, callback_data=f"station_{station}")] for station in fetch_metadata()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(  # Send a new message instead of editing the existing one
        f"Please select a station to fetch image from:",
        reply_markup=reply_markup
    )

async def send_location_image(query, context: ContextTypes.DEFAULT_TYPE, location: str) -> None:
    """Send the latest image of the selected location to the user.""" 
    location_images = {
        "bassac": 'https://www.khmertimeskh.com/wp-content/uploads/2024/08/Phnom-Penh-condos-riverside-living.jpg'
    }

    image_path = location_images.get(location, None)
    print(image_path)
    if image_path:
        await query.edit_message_text(  # Edit the original message instead of sending a new one
            text=f"Location: {location.replace('_', ' ').title()}",
            reply_markup=None  # Remove the keyboard
        )
        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=image_path,
            caption=f"Latest image of {location.replace('_', ' ').title()}",
            reply_to_message_id=query.message.message_id  # Link the photo to the original message
        )
    else:
        await query.edit_message_text("Sorry, no image available for this location.")

async def subscription_station_selection(query, is_unsubscribe: bool = False) -> None:
    """Prompt the user to select a station for subscription or unsubscription.""" 
    keyboard = [[InlineKeyboardButton(station, callback_data=f"location_{station.replace(' ', '_')}")] for station in fetch_metadata()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    action = "subscribe to" if not is_unsubscribe else "unsubscribe from"
    await query.message.reply_text(  # Send a new message instead of editing the existing one
        f"Please select a station to {action} daily flood alerts:",
        reply_markup=reply_markup
    )

async def manage_subscription(query, context: ContextTypes.DEFAULT_TYPE, location: str) -> None:
    """Manage the subscription status for the user based on the selected location."""
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    # Check if the user is unsubscribing or subscribing based on the presence of subscription data
    is_unsubscribe = user_manager.is_user_subscribed(user_id, location)

    if is_unsubscribe:
        # Unsubscribe the user from the selected location
        user_manager.unsubscribe_user(user_id, location)
        await query.edit_message_text(
            text=f"You have been unsubscribed from daily flood alerts for {location.replace('_', ' ').title()}."
        )
    else:
        # Subscribe the user to the selected location
        user_manager.subscribe_user(user_id, location)
        await query.edit_message_text(
            text=f"You have successfully subscribed to daily flood alerts for {location.replace('_', ' ').title()}."
        )

async def new_session(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new chat session""" 
    context.chat_data["system_prompt"] = FIXED_SYSTEM_PROMPT
    context.chat_data["conversation_id"] = chatbot.new_conversation(modelIndex=DEFAULT_MODEL_INDEX, system_prompt=FIXED_SYSTEM_PROMPT)
    await query.message.reply_text("New chat session started!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages""" 
    if "conversation_id" not in context.chat_data:
        context.chat_data["system_prompt"] = FIXED_SYSTEM_PROMPT
        context.chat_data["conversation_id"] = chatbot.new_conversation(modelIndex=DEFAULT_MODEL_INDEX, system_prompt=FIXED_SYSTEM_PROMPT)

    init_msg = await update.message.reply_text("Generating response...")

    conversation_id = context.chat_data["conversation_id"]
    chatbot.change_conversation(conversation_id)

    message = update.message.text
    if not message:
        return

    full_output_message = ""

    if context_data is None:
        await fetch_data(context)

    await update.message.chat.send_action(ChatAction.TYPING)
    for message in generate_response(message, context_data):
        if message:
            full_output_message += message
            send_message = format_message(full_output_message)
            init_msg = await init_msg.edit_text(send_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def broadcast_daily(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a daily broadcast message to all subscribed users for each station they are subscribed to."""
    subscribed_users = user_manager.get_subscribed_users()  # Get all users and their subscribed stations
    print(subscribed_users)
    
    for user_id, user_data in subscribed_users.items():
        chat_id = user_data['chat_id']
        
        for station in user_data['stations']:  # Loop through each station the user is subscribed to
            message = (
                f"🌊 **Daily Flood Report for {station}**\n\n"
                "Stay safe and updated on the current situation!\n\n"
                f"**Location**: {station}\n"
                f"**Water Level**: 10 meters\n"
                f"**Rainfall**: 10 mm/day\n"
                f"**Waterflow**: 10 L/s\n\n"
                "**Forecast**\n"
                f"Predicted Water Level: {predict_water_level()} meters\n\n"
                "Stay alert and take precautions if needed! 🚨"
            )
            
            try:
                await context.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                print(f"Error sending message to {chat_id}: {e}")


async def fetch_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    global context_data

    
    try:
        forecast_data = predict_water_level(forward_days=5)
    except (KeyError, IndexError, TypeError):
        forecast_data = None

    try:
        water_level = fetch_measurement(station="bassac", range="15d", measurement="water_level")['data'][-1]
    except (KeyError, IndexError, TypeError):
        water_level = None

    try:
        rainfall = fetch_measurement(station="bassac", range="15d", measurement="rainfall")['data'][-1]
    except (KeyError, IndexError, TypeError):
        rainfall = None

    try:
        water_flow = fetch_measurement(station="bassac", range="15d", measurement="water_flow")['data'][-1]
    except (KeyError, IndexError, TypeError):
        water_flow = None

    print("Forecast Data:", forecast_data)
    print("Water Level:", water_level)
    print("Rainfall:", rainfall)
    print("Water Flow:", water_flow)

    context_data = {
        "forecast_info": forecast_data if forecast_data else "Forecast data is unavailable at the moment.",
        "water_level_info": water_level if water_level else "Water Level is unavailable at the moment.",
        "rainfall_info": rainfall if rainfall else "Rainfall data is unavailable at the moment.",
        "water_flow_info": water_flow if water_flow else "Water Flow is unavailable at the moment."
    }

    print(context_data)
    