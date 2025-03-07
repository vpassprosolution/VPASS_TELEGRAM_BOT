import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# API URL for VPASS AI TECHNICAL
API_URL = "https://vpassaitechnical-production.up.railway.app/chart/"

def show_technical_menu(update: Update, context: CallbackContext) -> None:
    """Show the instrument selection menu for AI Technical Analysis."""
    keyboard = [
        [InlineKeyboardButton("📊 Gold", callback_data="technical_gold")],
        [InlineKeyboardButton("📊 Bitcoin", callback_data="technical_bitcoin")],
        [InlineKeyboardButton("📊 Ethereum", callback_data="technical_ethereum")],
        [InlineKeyboardButton("📊 Dow Jones", callback_data="technical_dowjones")],
        [InlineKeyboardButton("📊 Nasdaq", callback_data="technical_nasdaq")],
        [InlineKeyboardButton("📊 EUR/USD", callback_data="technical_eurusd")],
        [InlineKeyboardButton("📊 GBP/USD", callback_data="technical_gbpusd")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("📊 **Select an Instrument for AI Technical Analysis**:", reply_markup=reply_markup)

def handle_technical_selection(update: Update, context: CallbackContext) -> None:
    """Handle instrument selection and send chart."""
    query = update.callback_query
    instrument_map = {
        "technical_gold": "gold",
        "technical_bitcoin": "bitcoin",
        "technical_ethereum": "ethereum",
        "technical_dowjones": "dow jones",
        "technical_nasdaq": "nasdaq",
        "technical_eurusd": "eur/usd",
        "technical_gbpusd": "gbp/usd"
    }

    instrument_key = query.data
    if instrument_key not in instrument_map:
        query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    instrument = instrument_map[instrument_key]
    timeframe = "1h"  # Default to 1-hour timeframe for now

    # Call the AI Technical API
    response = requests.get(API_URL, params={"instrument": instrument, "timeframe": timeframe})

    if response.status_code == 200:
        chart_url = response.json().get("chart_url")

        if chart_url:
            query.message.reply_photo(photo=chart_url, caption=f"📊 {instrument.upper()} 1H Chart")
        else:
            query.message.reply_text("❌ Failed to retrieve chart. Please try again.")
    else:
        query.message.reply_text("❌ Error retrieving chart. Please try again.")
