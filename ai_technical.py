import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# API URL for VPASS AI TECHNICAL
API_URL = "https://vpassaitechnical-production.up.railway.app/chart/"

async def show_technical_menu(update: Update, context: CallbackContext) -> None:
    """Show the instrument selection menu for AI Technical Analysis."""
    keyboard = [
        [InlineKeyboardButton("📊 Gold", callback_data="instrument_gold")],
        [InlineKeyboardButton("📊 Bitcoin", callback_data="instrument_bitcoin")],
        [InlineKeyboardButton("📊 Ethereum", callback_data="instrument_ethereum")],
        [InlineKeyboardButton("📊 Dow Jones", callback_data="instrument_dowjones")],
        [InlineKeyboardButton("📊 Nasdaq", callback_data="instrument_nasdaq")],
        [InlineKeyboardButton("📊 EUR/USD", callback_data="instrument_eurusd")],
        [InlineKeyboardButton("📊 GBP/USD", callback_data="instrument_gbpusd")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("📊 **Select an Instrument for AI Technical Analysis**:", reply_markup=reply_markup)

async def show_timeframe_menu(update: Update, context: CallbackContext) -> None:
    """Show the timeframe selection menu after choosing an instrument."""
    query = update.callback_query
    instrument_map = {
        "instrument_gold": "gold",
        "instrument_bitcoin": "bitcoin",
        "instrument_ethereum": "ethereum",
        "instrument_dowjones": "dow jones",
        "instrument_nasdaq": "nasdaq",
        "instrument_eurusd": "eur/usd",
        "instrument_gbpusd": "gbp/usd"
    }

    instrument_key = query.data
    if instrument_key not in instrument_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    # Store selected instrument in user context
    context.user_data["selected_instrument"] = instrument_map[instrument_key]

    keyboard = [
        [InlineKeyboardButton("⏳ 5M", callback_data="timeframe_5m")],
        [InlineKeyboardButton("⏳ 15M", callback_data="timeframe_15m")],
        [InlineKeyboardButton("⏳ 30M", callback_data="timeframe_30m")],
        [InlineKeyboardButton("⏳ 1H", callback_data="timeframe_1h")],
        [InlineKeyboardButton("⏳ 4H", callback_data="timeframe_4h")],
        [InlineKeyboardButton("⏳ 1D", callback_data="timeframe_1d")],
        [InlineKeyboardButton("🔙 Back", callback_data="ai_technical")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(f"📊 **Selected: {context.user_data['selected_instrument'].upper()}**\n\nNow choose a timeframe:", reply_markup=reply_markup)

async def handle_technical_selection(update: Update, context: CallbackContext) -> None:
    """Handle timeframe selection and send chart."""
    query = update.callback_query

    if "selected_instrument" not in context.user_data:
        await query.message.reply_text("❌ No instrument selected. Please go back and choose one.")
        return

    instrument = context.user_data["selected_instrument"]
    timeframe_map = {
        "timeframe_5m": "5m",
        "timeframe_15m": "15m",
        "timeframe_30m": "30m",
        "timeframe_1h": "1h",
        "timeframe_4h": "4h",
        "timeframe_1d": "1d"
    }

    timeframe_key = query.data
    if timeframe_key not in timeframe_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    timeframe = timeframe_map[timeframe_key]

    # Call the AI Technical API
    response = requests.get(API_URL, params={"instrument": instrument, "timeframe": timeframe})

    if response.status_code == 200:
        chart_url = response.json().get("chart_url")

        if chart_url:
            await query.message.reply_photo(photo=chart_url, caption=f"📊 {instrument.upper()} {timeframe.upper()} Chart")
        else:
            await query.message.reply_text("❌ Failed to retrieve chart. Please try again.")
    else:
        await query.message.reply_text("❌ Error retrieving chart. Please try again.")
