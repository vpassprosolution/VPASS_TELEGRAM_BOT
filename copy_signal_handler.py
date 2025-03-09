import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

API_URL = "https://vpasscopysignal-production.up.railway.app"

# Function to show subscription menu when button is clicked
async def handle_copy_signal(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("Subscribe ✅", callback_data="subscribe")],
        [InlineKeyboardButton("Unsubscribe ❌", callback_data="unsubscribe")],
        [InlineKeyboardButton("⬅ Back", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📡 *VPASS COPY SIGNAL*\nChoose an option:", parse_mode="Markdown", reply_markup=reply_markup)

# Function to handle subscription
async def subscribe_user(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    data = {
        "user_id": user_id,
        "group_id": -1001234567890,  # Replace with actual group ID
        "signal_format": "Gold Buy/Sell"
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
    user_id = query.message.chat_id
    data = {"user_id": user_id}
    response = requests.post(f"{API_URL}/unsubscribe", json=data)

    if response.status_code == 200:
        await query.answer("✅ Unsubscription successful!")
        await query.message.edit_text("✅ You have successfully unsubscribed!")
    else:
        await query.answer("❌ Unsubscription failed. Try again.")
