import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# VPASS_NEWS_WAR_ROOM API URL
API_BASE_URL = "https://vpassnewswarroom-production.up.railway.app"

# Function: Check Subscription Status
def check_subscription(user_id):
    response = requests.get(f"{API_BASE_URL}/check_subscription?user_id={user_id}")
    data = response.json()
    return data.get("subscribed", False)

# Function: Subscribe User
async def subscribe_user(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    payload = {"user_id": user.id, "username": user.username}

    response = requests.post(f"{API_BASE_URL}/subscribe", json=payload)
    message = response.json().get("message", "Something went wrong.")

    # Add Back Button
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="news_war_room")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

# Function: Unsubscribe User
async def unsubscribe_user(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    payload = {"user_id": user.id}

    response = requests.post(f"{API_BASE_URL}/unsubscribe", json=payload)
    message = response.json().get("message", "Something went wrong.")

    # Add Back Button
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="news_war_room")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

# Function: Show News War Room Menu
async def show_news_war_room(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    is_subscribed = check_subscription(user_id)

    keyboard = [
        [
            InlineKeyboardButton("✅ Subscribe", callback_data="subscribe_news") if not is_subscribed else 
            InlineKeyboardButton("❌ Unsubscribe", callback_data="unsubscribe_news"),
            InlineKeyboardButton("ℹ️ About News War Room", callback_data="about_news_war_room")
        ],
        [InlineKeyboardButton("💬 Enter Chat Room", callback_data="enter_chat")],  # Button to enter chat
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]  # Back to Main Menu
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("🔴 **NEWS WAR ROOM** 🔴\n📢 Get real-time alerts for high-impact USD news.", reply_markup=reply_markup)

# Function: Show About News War Room Info
async def show_about_news_war_room(update: Update, context: CallbackContext):
    query = update.callback_query

    message = (
        "📢 **ABOUT NEWS WAR ROOM** 📢\n\n"
        "🔥 **What is the News War Room?**\n"
        "It is a real-time alert system that notifies traders before and after high-impact USD news events.\n\n"
        "🛠 **How It Works:**\n"
        "✅ Get a reminder **24 hours before** the news.\n"
        "✅ Receive a **final alert 1 hour before** the event.\n"
        "✅ A **live alert** when the news is released.\n\n"
        "⚙️ **Why Join?**\n"
        "✔️ Stay ahead of the market.\n"
        "✔️ Make informed trading decisions.\n"
        "✔️ Exclusive to subscribers only.\n\n"
        "📌 Click **Back** to return."
    )

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="news_war_room")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, parse_mode="Markdown", reply_markup=reply_markup)

# Function: Handle Chat Room Entry
async def enter_chat_room(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Notify users about chat rules
    message = (
        "💬 **Welcome to the NEWS WAR ROOM Chat** 💬\n\n"
        "🔹 You can discuss the upcoming news here.\n"
        "🔹 The chat will be closed **20 minutes after news is released**.\n"
        "🔹 Stay respectful and share valuable insights!\n\n"
        "🚀 **Happy Trading!**"
    )

    await query.edit_message_text(message)

# Handle Button Clicks
async def news_war_room_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "subscribe_news":
        await subscribe_user(update, context)
    elif query.data == "unsubscribe_news":
        await unsubscribe_user(update, context)
    elif query.data == "about_news_war_room":
        await show_about_news_war_room(update, context)
    elif query.data == "enter_chat":
        await enter_chat_room(update, context)
    elif query.data == "main_menu":
        from bot import main_menu
        await main_menu(update, context)
