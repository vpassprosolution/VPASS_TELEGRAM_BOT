import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import asyncio

# API URL for VPASS AI TECHNICAL
API_URL = "https://vpassaitechnical-production.up.railway.app/chart/"

# Categories Menu
async def show_category_menu(update: Update, context: CallbackContext) -> None:
    """Show category selection menu for AI Technical Analysis."""
    keyboard = [
        [InlineKeyboardButton("📌 Forex", callback_data="category_forex")],
        [InlineKeyboardButton("📌 Metals", callback_data="category_metals")],
        [InlineKeyboardButton("📌 Index", callback_data="category_index")],
        [InlineKeyboardButton("📌 Crypto", callback_data="category_crypto")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("📊 **Select a Category**:", reply_markup=reply_markup, parse_mode="Markdown")

# Instruments Menu
async def show_instrument_menu(update: Update, context: CallbackContext) -> None:
    """Show instrument selection menu based on category."""
    query = update.callback_query
    category_map = {
        "category_forex": [
            ("EUR/USD", "instrument_eurusd"), ("GBP/USD", "instrument_gbpusd"),
            ("USD/JPY", "instrument_usdjpy"), ("USD/CHF", "instrument_usdchf"),
            ("USD/CAD", "instrument_usdcad"), ("AUD/USD", "instrument_audusd"),
            ("NZD/USD", "instrument_nzdusd"), ("EUR/JPY", "instrument_eurjpy"),
            ("GBP/JPY", "instrument_gbpjpy"), ("EUR/GBP", "instrument_eurgbp")
        ],
        "category_metals": [
            ("Gold", "instrument_xauusd"), ("Silver", "instrument_xagusd"),
            ("Platinum", "instrument_xptusd"), ("Palladium", "instrument_xpdusd"),
            ("Copper", "instrument_xcuusd")
        ],
        "category_index": [
            ("Dow Jones", "instrument_dji"), ("NASDAQ", "instrument_ixic"),
            ("S&P 500", "instrument_spx"), ("FTSE 100", "instrument_uk100"),
            ("DAX", "instrument_de30"), ("Nikkei 225", "instrument_jp225"),
            ("Hang Seng", "instrument_hk50"), ("CAC 40", "instrument_fra40"),
            ("ASX 200", "instrument_aus200"), ("Russell 2000", "instrument_rut")
        ],
        "category_crypto": [
            ("Bitcoin", "instrument_btcusd"), ("Ethereum", "instrument_ethusd"),
            ("XRP", "instrument_xrpusd"), ("Litecoin", "instrument_ltcusd"),
            ("Cardano", "instrument_adausd"), ("Solana", "instrument_solusd"),
            ("Binance", "instrument_bnbusd"), ("Dogecoin", "instrument_dogeusd"),
            ("Polkadot", "instrument_dotusd"), ("Avalanche", "instrument_avaxusd")
        ]
    }

    category_key = query.data
    if category_key not in category_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    keyboard = [[InlineKeyboardButton(name, callback_data=callback)] for name, callback in category_map[category_key]]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_categories")])

    # Store selected category in user context
    context.user_data["selected_category"] = category_key
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📊 **Select an Instrument**:", reply_markup=reply_markup, parse_mode="Markdown")

# Timeframe Menu
async def show_timeframe_menu(update: Update, context: CallbackContext) -> None:
    """Show the timeframe selection menu after choosing an instrument."""
    query = update.callback_query
    instrument_map = {
        # Forex
        "instrument_eurusd": "EUR/USD (EURUSD)", "instrument_gbpusd": "GBP/USD (GBPUSD)",
        "instrument_usdjpy": "USD/JPY (USDJPY)", "instrument_usdchf": "USD/CHF (USDCHF)",
        "instrument_usdcad": "USD/CAD (USDCAD)", "instrument_audusd": "AUD/USD (AUDUSD)",
        "instrument_nzdusd": "NZD/USD (NZDUSD)", "instrument_eurjpy": "EUR/JPY (EURJPY)",
        "instrument_gbpjpy": "GBP/JPY (GBPJPY)", "instrument_eurgbp": "EUR/GBP (EURGBP)",

        # Metals
        "instrument_xauusd": "Gold (XAUUSD)", "instrument_xagusd": "Silver (XAGUSD)",
        "instrument_xptusd": "Platinum (XPTUSD)", "instrument_xpdusd": "Palladium (XPDUSD)",
        "instrument_xcuusd": "Copper (XCUUSD)",

        # Index & Crypto (continued inside the function)
    }

    if query.data not in instrument_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    # Store selected instrument in user context
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
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_instruments")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(f"📊 **Selected: {context.user_data['selected_instrument']}**\n\nNow choose a timeframe:", reply_markup=reply_markup, parse_mode="Markdown")
