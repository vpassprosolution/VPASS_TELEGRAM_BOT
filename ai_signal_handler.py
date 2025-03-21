import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler


# AI API URL (Replace with your actual Railway URL)
AI_API_URL = "https://aiagentinstantsignal-production.up.railway.app"

# Function to fetch trade signal from the AI API
async def fetch_ai_signal(update: Update, context: CallbackContext):
    selected_instrument = update.callback_query.data.replace("ai_signal_", "")

    # ✅ Fix: Ensure Gold (XAUUSD) is correctly mapped
    if selected_instrument == "XAU":
        selected_instrument = "XAUUSD"

    response = requests.get(f"{AI_API_URL}/get_signal/{selected_instrument}")

    if response.status_code == 200:
        trade_signal = response.json().get("signal", "⚠️ No Signal Available")
    else:
        trade_signal = "⚠️ Error fetching signal"

    # ✅ Fix Output Format - Directly Show AI-Generated Signal Without Extra Duplicates
    formatted_message = f"⚡ *{selected_instrument}* Signal:\n{trade_signal}"

    # ✅ Add a Back button to return to the instrument selection
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ai_agent_signal")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # ✅ Send the formatted message with Markdown enabled
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(
        formatted_message, 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )

# Function to show instrument selection buttons
async def show_instruments(update, context):
    keyboard = [
        [InlineKeyboardButton("🏆 Gold", callback_data="ai_signal_XAUUSD")],  # ✅ Fixed: Now correctly calls XAUUSD
        [InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="ai_signal_BTC"), InlineKeyboardButton("🪙 ETHEREUM (ETH)", callback_data="ai_signal_ETH")],
        [InlineKeyboardButton("📊 Dow Jones (DJI)", callback_data="ai_signal_DJI"), InlineKeyboardButton("📊 NASDAQ (IXIC)", callback_data="ai_signal_IXIC")],
        [InlineKeyboardButton("💶 EUR/USD (EURUSD)", callback_data="ai_signal_EURUSD"), InlineKeyboardButton("💷 GBP/USD (GBPUSD)", callback_data="ai_signal_GBPUSD")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]  # Back button
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.edit_text(
        "Select Your Exclusive Instrument for Elite AI Insights 💎📈",
        reply_markup=reply_markup
    )

# Callback Query Handlers
ai_signal_handler = CallbackQueryHandler(fetch_ai_signal, pattern='^ai_signal_')
instrument_menu_handler = CallbackQueryHandler(show_instruments, pattern='^ai_agent_signal$')  # ✅ Fixed function name
