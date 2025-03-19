import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import asyncio

# API URL for VPASS AI TECHNICAL
API_URL = "https://vpassaitechnical-production.up.railway.app/chart/"

# Categories Menu
async def show_technical_menu(update: Update, context: CallbackContext) -> None:
    """Show category selection menu for AI Technical Analysis."""
    keyboard = [
        [InlineKeyboardButton("📌 Forex", callback_data="category_forex"),
         InlineKeyboardButton("📌 Metals", callback_data="category_metals")],
        [InlineKeyboardButton("📌 Index", callback_data="category_index"),
         InlineKeyboardButton("📌 Crypto", callback_data="category_crypto")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("📊 **Select a Category**:", reply_markup=reply_markup, parse_mode="Markdown")

# Instruments Menu
async def show_instrument_menu(update: Update, context: CallbackContext) -> None:
    """Show instrument selection menu based on category."""
    query = update.callback_query
    category_key = query.data

    category_map = {
        "category_forex": [
            ("EUR/USD", "instrument_eurusd"), ("GBP/USD", "instrument_gbpusd"), ("USD/JPY", "instrument_usdjpy"),
            ("USD/CHF", "instrument_usdchf"), ("USD/CAD", "instrument_usdcad"), ("AUD/USD", "instrument_audusd"),
            ("NZD/USD", "instrument_nzdusd"), ("EUR/JPY", "instrument_eurjpy"), ("GBP/JPY", "instrument_gbpjpy"),
            ("EUR/GBP", "instrument_eurgbp")
        ],
        "category_metals": [
            ("Gold", "instrument_xauusd"), ("Silver", "instrument_xagusd"), ("Platinum", "instrument_xptusd"),
            ("Palladium", "instrument_xpdusd"), ("Copper", "instrument_xcuusd")
        ],
        "category_index": [
            ("Dow Jones", "instrument_dji"), ("NASDAQ", "instrument_ixic"), ("S&P 500", "instrument_spx"),
            ("FTSE 100", "instrument_uk100"), ("DAX", "instrument_de30"), ("Nikkei 225", "instrument_jp225"),
            ("Hang Seng", "instrument_hk50"), ("CAC 40", "instrument_fra40"), ("ASX 200", "instrument_aus200"),
            ("Russell 2000", "instrument_rut")
        ],
        "category_crypto": [
            ("Bitcoin", "instrument_btcusd"), ("Ethereum", "instrument_ethusd"), ("XRP", "instrument_xrpusd"),
            ("Litecoin", "instrument_ltcusd"), ("Cardano", "instrument_adausd"), ("Solana", "instrument_solusd"),
            ("Binance", "instrument_bnbusd"), ("Dogecoin", "instrument_dogeusd"), ("Polkadot", "instrument_dotusd"),
            ("Avalanche", "instrument_avaxusd")
        ]
    }

    if category_key not in category_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    context.user_data["selected_category"] = category_key

    keyboard = []
    instruments = category_map[category_key]
    for i in range(0, len(instruments), 3):
        keyboard.append([InlineKeyboardButton(name, callback_data=callback) for name, callback in instruments[i:i+3]])

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_technical_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📊 **Select an Instrument**:", reply_markup=reply_markup, parse_mode="Markdown")

# Timeframe Menu (Back Button Goes to 4 Categories)
async def show_timeframe_menu(update: Update, context: CallbackContext) -> None:
    """Show the timeframe selection menu after choosing an instrument."""
    query = update.callback_query

    instrument_map = {
        "instrument_eurusd": "EUR/USD", "instrument_gbpusd": "GBP/USD", "instrument_usdjpy": "USD/JPY",
        "instrument_usdchf": "USD/CHF", "instrument_usdcad": "USD/CAD", "instrument_audusd": "AUD/USD",
        "instrument_nzdusd": "NZD/USD", "instrument_eurjpy": "EUR/JPY", "instrument_gbpjpy": "GBP/JPY",
        "instrument_eurgbp": "EUR/GBP", "instrument_xauusd": "Gold", "instrument_xagusd": "Silver",
        "instrument_xptusd": "Platinum", "instrument_xpdusd": "Palladium", "instrument_xcuusd": "Copper"
    }

    # Validate instrument selection
    if query.data not in instrument_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    context.user_data["selected_instrument"] = instrument_map[query.data]

    keyboard = [
        [InlineKeyboardButton("⏳ M1", callback_data="timeframe_1m"),
         InlineKeyboardButton("⏳ M5", callback_data="timeframe_5m"),
         InlineKeyboardButton("⏳ M15", callback_data="timeframe_15m")],
        [InlineKeyboardButton("⏳ M30", callback_data="timeframe_30m"),
         InlineKeyboardButton("⏳ H1", callback_data="timeframe_1h"),
         InlineKeyboardButton("⏳ H4", callback_data="timeframe_4h")],
        [InlineKeyboardButton("⏳ Weekly", callback_data="timeframe_1w"),
         InlineKeyboardButton("⏳ Monthly", callback_data="timeframe_1mo")],
        [InlineKeyboardButton("🔙 Back to Categories", callback_data="back_to_technical_menu")]  # ✅ Now goes back to 4 categories
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(f"📊 **Selected: {context.user_data['selected_instrument']}**\n\nNow choose a timeframe:", reply_markup=reply_markup, parse_mode="Markdown")



# Back to Category Menu
async def back_to_technical_menu(update: Update, context: CallbackContext) -> None:
    """Handles the back button from instrument selection to category selection."""
    await show_technical_menu(update, context)

# Handle Timeframe Selection
async def handle_technical_selection(update: Update, context: CallbackContext) -> None:
    """Handles timeframe selection and sends the TradingView chart from the API."""
    query = update.callback_query

    if "selected_instrument" not in context.user_data:
        await query.message.reply_text("❌ No instrument selected. Please go back and choose one.")
        return

    instrument = context.user_data["selected_instrument"]
    timeframe_map = {
        "timeframe_1m": "1m",
        "timeframe_5m": "5m",
        "timeframe_15m": "15m",
        "timeframe_30m": "30m",
        "timeframe_1h": "1h",
        "timeframe_4h": "4h",
        "timeframe_1w": "1w",
        "timeframe_1mo": "1mo"
    }

    timeframe_key = query.data
    if timeframe_key not in timeframe_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    response = requests.get(API_URL, params={"instrument": instrument, "timeframe": timeframe_map[timeframe_key]})

    if response.status_code == 200:
        chart_url = response.json().get("chart_url")
        if chart_url:
            await query.message.reply_photo(photo=chart_url, caption=f"📊 {instrument} {timeframe_map[timeframe_key].upper()} Chart")
        else:
            await query.message.reply_text("❌ Chart not available. Please try again later.")
    else:
        await query.message.reply_text("❌ Error retrieving chart. Please try again.")



# Back to 4 Categories Menu
async def back_to_technical_menu(update: Update, context: CallbackContext) -> None:
    """Handles the back button from timeframe selection to the 4 categories menu."""
    await show_technical_menu(update, context)  # ✅ Now correctly sends user back to category selection

