import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# VPASS_NEWS_WAR_ROOM API URL
API_BASE_URL = "https://vpassnewswarroom-production.up.railway.app"

# Function: Check Subscription Status
def check_subscription(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/check_subscription?user_id={user_id}")
        response.raise_for_status()
        data = response.json()

        # ✅ Debugging log to verify API response
        print(f"🔍 Subscription API Response for {user_id}: {data}")

        return data.get("subscribed", False)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking subscription: {e}")
        return False



# Function: Subscribe User
async def subscribe_user(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    payload = {"user_id": user.id, "username": user.username}

    try:
        response = requests.post(f"{API_BASE_URL}/subscribe", json=payload)
        if response.status_code != 200 or not response.text.strip():
            raise ValueError("Invalid response from API")

        message = response.json().get("message", "Subscription successful.")
    except (requests.exceptions.RequestException, ValueError) as e:
        message = f"❌ Subscription failed: {e}"

    # Refresh the News War Room menu after subscribing
    await show_news_war_room(update, context)


    # Add Back Button
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="news_war_room")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

# Function: Unsubscribe User
async def unsubscribe_user(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    payload = {"user_id": user.id}

    try:
        response = requests.post(f"{API_BASE_URL}/unsubscribe", json=payload)
        if response.status_code != 200 or not response.text.strip():
            raise ValueError("Invalid response from API")

        message = response.json().get("message", "Unsubscription successful.")
    except (requests.exceptions.RequestException, ValueError) as e:
        message = f"❌ Unsubscription failed: {e}"

    # Refresh the News War Room menu after unsubscribing
    await show_news_war_room(update, context)


    # Add Back Button
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="news_war_room")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)


# Function: Show News War Room Menu
async def show_news_war_room(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    # ✅ Force refresh the subscription status from API
    is_subscribed = check_subscription(user_id)

    # ✅ Debugging log (Check what is returned)
    print(f"🔍 User {user_id} Subscription Status: {is_subscribed}")

    keyboard = [
        [
            InlineKeyboardButton("✅ Subscribe", callback_data="subscribe_news") if not is_subscribed else 
            InlineKeyboardButton("❌ Unsubscribe", callback_data="unsubscribe_news"),
            InlineKeyboardButton("ℹ️ About News War Room", callback_data="about_news_war_room")
        ],
        [InlineKeyboardButton("💬 Enter Chat Room", callback_data="enter_chat")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # ✅ Ensure we force a refresh instead of using old data
        await query.message.edit_text("🔴 **NEWS WAR ROOM** 🔴\n📢 Get real-time alerts for high-impact USD news.", reply_markup=reply_markup)
    except Exception as e:
        print(f"❌ Error updating message: {e}")


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
    user_id = query.from_user.id

    message = (
        "💬 **Welcome to the NEWS WAR ROOM Chat** 💬\n\n"
        "🔹 You can discuss the upcoming news here.\n"
        "🔹 The chat will close **20 minutes after news is released**.\n"
        "🔹 Stay respectful and share valuable insights!\n\n"
        "💬 Send a message, and it will be shared with all users!"
    )

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="news_war_room")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

async def forward_chat_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    message = update.message.text

    if not message:
        return

    # Send message to API for broadcasting
    api_url = "https://vpassnewswarroom-production.up.railway.app/send_chat_message"
    requests.post(api_url, json={"user_id": user.id, "message": f"{user.first_name}: {message}"})


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
        try:
            from bot import main_menu
            await main_menu(update, context)
        except ImportError:
            await query.message.edit_text("⚠️ Error: Main Menu function not found!")
