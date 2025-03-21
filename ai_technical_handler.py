from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import requests

# ✅ Your deployed Railway API endpoint
API_URL = "https://ai-technical.up.railway.app/get_chart_image"

# ✅ Instruments grouped by category
INSTRUMENTS = {
    "Forex": [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "USDCAD", "EURGBP",
        "EURCAD", "AUDJPY", "NZDJPY", "CHFJPY", "USDHKD", "USDZAR", "USDNOK", "USDSEK", "EURNZD", "GBPAUD"
    ],
    "Crypto": [
        "BTCUSDT", "ETHUSDT", "XRPUSDT", "LTCUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT",
        "TRXUSDT", "LINKUSDT", "MATICUSDT", "FILUSDT", "SHIBUSDT", "ATOMUSDT", "EOSUSDT", "NEARUSDT", "XLMUSDT", "ALGOUSDT"
    ],
    "Index": [
        "DJI", "IXIC", "SPX", "UK100", "DE30", "FR40", "JP225", "HK50", "AUS200", "CHINA50",
        "IT40", "NL25", "STOXX50", "TW50", "KRX100", "BRLSP", "MEXBOL", "RTS", "NSEI", "BIST100"
    ],
    "MetalsOil": ["XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD", "WTI"]
}

TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W", "1M"]

# ✅ Step 1: Show Categories
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton(cat, callback_data=f"ai_cat_{cat}")] for cat in INSTRUMENTS]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])

    await query.message.edit_text("📊 *Select a Market Category:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ✅ Step 2: Show Instruments
async def show_instruments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("ai_cat_", "")
    instruments = INSTRUMENTS.get(category, [])

    keyboard = [[InlineKeyboardButton(symbol, callback_data=f"ai_symbol_{category}_{symbol}")] for symbol in instruments]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="ai_technical")])

    await query.message.edit_text(f"💹 *Select an Instrument from {category}:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ✅ Step 3: Show Timeframes
async def show_timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, category, symbol = query.data.split("_", 2)
    keyboard = [[InlineKeyboardButton(tf, callback_data=f"ai_chart_{symbol}_{tf}")] for tf in TIMEFRAMES]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"ai_cat_{category}")])

    await query.message.edit_text(f"🕒 *Select Timeframe for {symbol}:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ✅ Step 4: Call API and Send Chart
async def fetch_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, symbol, tf = query.data.split("_", 2)
    full_symbol = f"BINANCE:{symbol}" if "USDT" in symbol else f"OANDA:{symbol}"

    payload = {"symbol": full_symbol, "interval": tf}

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            image_path = response.json().get("chart_image")
            await query.message.reply_photo(photo=open(image_path, "rb"), caption=f"{symbol} ({tf}) Chart")
        else:
            await query.message.reply_text("⚠️ Failed to fetch chart. Please try again.")
    except Exception:
        await query.message.reply_text("❌ Server error. Try again later.")
