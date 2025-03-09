import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

API_URL = "https://vpasscopysignal-production.up.railway.app"

# Function to show copy signal options
async def handle_copy_signal(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("📢 Another Telegram Group", callback_data="copy_telegram")],
        [InlineKeyboardButton("📈 TradingView (Coming Soon)", callback_data="ignore")],
        [InlineKeyboardButton("⬅ Back", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📡 *Choose Your Copy Signal Source:*", parse_mode="Markdown", reply_markup=reply_markup)

# Function to ask for the Telegram group link
async def ask_group_link(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("⬅ Back", callback_data="vpass_copy_signal")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("🔗 Please send the Telegram group link where you want to copy signals from:", reply_markup=reply_markup)
    context.user_data["waiting_for_group_link"] = True

# Function to collect the group link
async def collect_group_link(update: Update, context: CallbackContext) -> None:
    if "waiting_for_group_link" in context.user_data:
        group_link = update.message.text
        context.user_data["group_link"] = group_link
        del context.user_data["waiting_for_group_link"]
        await update.message.reply_text("✅ Group link saved! Now, please enter the format of signals from this group:")
        context.user_data["waiting_for_signal_format"] = True

# Function to collect the signal format
async def collect_signal_format(update: Update, context: CallbackContext) -> None:
    if "waiting_for_signal_format" in context.user_data:
        signal_format = update.message.text
        group_link = context.user_data.get("group_link", "Not provided")
        del context.user_data["waiting_for_signal_format"]
        await update.message.reply_text(f"✅ Format saved!\n\n🔗 *Group Link:* {group_link}\n📊 *Signal Format:* {signal_format}\n\nNow, click 'Subscribe' to start receiving signals.")
        
        # Store group link & format for subscription
        context.user_data["signal_data"] = {"group_link": group_link, "signal_format": signal_format}

        # Show subscribe button
        keyboard = [[InlineKeyboardButton("✅ Subscribe", callback_data="subscribe")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Click below to subscribe:", reply_markup=reply_markup)

# Function to handle subscription
async def subscribe_user(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id  # ✅ FIXED: Use from_user.id instead of message.chat_id

    # Get stored group link & signal format
    signal_data = context.user_data.get("signal_data", {})
    group_link = signal_data.get("group_link", "Unknown")
    signal_format = signal_data.get("signal_format", "Unknown")

    data = {
        "user_id": user_id,
        "group_link": group_link,
        "signal_format": signal_format
    }
    
    response = requests.post(f"{API_URL}/subscribe", json=data)

    if response.status_code == 200:
        await query.answer("✅ Subscription successful!")
        await query.message.edit_text("✅ You have successfully subscribed!")
    else:
        await query.answer("❌ Subscription failed. Try again.")

# Function to handle unsubscription
async def unsubscribe_user(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id  # ✅ FIXED: Use from_user.id
    data = {"user_id": user_id}
    
    response = requests.post(f"{API_URL}/unsubscribe", json=data)

    if response.status_code == 200:
        await query.answer("✅ Unsubscription successful!")
        await query.message.edit_text("✅ You have successfully unsubscribed!")
    else:
        await query.answer("❌ Unsubscription failed. Try again.")
