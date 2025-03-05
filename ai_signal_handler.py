import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler

# AI API URL (Replace with your actual Railway URL)
AI_API_URL = "https://aiagentinstantsignal-production.up.railway.app"

# Function to fetch trade signal from the AI API
async def fetch_ai_signal(update: Update, context: CallbackContext):
    selected_instrument = update.callback_query.data.split('_')[1]  # Extract instrument from callback
    response = requests.get(f"{AI_API_URL}/get_signal/{selected_instrument}")

    if response.status_code == 200:
        trade_signal = response.json().get("signal", "⚠️ No Signal Available")
    else:
        trade_signal = "⚠️ Error fetching signal"

    # Send the trade signal as a response
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(f"Trade Signal for {selected_instrument}: {trade_signal}")

# Function to display instrument selection buttons
async def show_instrument_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Bitcoin (BTC)", callback_data='ai_signal_BTC')],
        [InlineKeyboardButton("Ethereum (ETH)", callback_data='ai_signal_ETH')],
        [InlineKeyboardButton("EUR/USD", callback_data='ai_signal_EURUSD')],
        [InlineKeyboardButton("GBP/USD", callback_data='ai_signal_GBPUSD')],
        [InlineKeyboardButton("Dow Jones (DJI)", callback_data='ai_signal_DJI')],
        [InlineKeyboardButton("Nasdaq (IXIC)", callback_data='ai_signal_IXIC')],
        [InlineKeyboardButton("Gold (XAU/USD)", callback_data='ai_signal_XAU')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        "Select an instrument to get the AI Agent Signal:",
        reply_markup=reply_markup
    )

# Callback Query Handlers
ai_signal_handler = CallbackQueryHandler(fetch_ai_signal, pattern='^ai_signal_')
instrument_menu_handler = CallbackQueryHandler(show_instrument_menu, pattern='^ai_agent_signal$')
