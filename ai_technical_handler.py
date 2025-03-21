from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import requests

API_URL = "https://ai-technical.up.railway.app/get_chart_image"

INSTRUMENTS = {
    "Forex": [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
        "NZDUSD", "EURJPY", "GBPJPY", "USDCAD", "EURGBP",
        "EURCAD", "AUDJPY", "NZDJPY", "CHFJPY", "USDHKD",
        "USDZAR", "USDNOK", "USDSEK", "EURNZD", "GBPAUD"
    ],
    "Crypto": [
        "BTCUSDT", "ETHUSDT", "XRPUSDT", "LTCUSDT", "BNBUSDT",
        "ADAUSDT", "SOLUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT",
        "TRXUSDT", "LINKUSDT", "MATICUSDT", "FILUSDT", "SHIBUSDT",
        "ATOMUSDT", "EOSUSDT", "NEARUSDT", "XLMUSDT", "ALGOUSDT"
    ],
    "Index": [
        "DJI", "IXIC", "SPX", "UK100", "DE30",
        "FR40", "JP225", "HK50", "AUS200", "CHINA50",
        "IT40", "NL25", "STOXX50", "TW50", "KRX100",
        "BRLSP", "MEXBOL", "RTS", "NSEI", "BIST100"
    ],
    "MetalsOil": ["XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD", "WTI"]
}

TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W", "1M"]

# Step 1: Show Categories
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rows = []
    categories = list(INSTRUMENTS.keys())
    for i in range(0, len(categories), 2):
        row = [InlineKeyboardButton(cat, callback_data=f"tech2_cat_{cat}") for cat in categories[i:i+2]]
        rows.append(row)

    rows.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    await query.message.edit_text("📊 *Select a Market Category:*", reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")


# Step 2: Show Instruments
async def show_technical_instruments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("tech2_cat_", "")
    instruments = INSTRUMENTS.get(category, [])

    keyboard = []

    if category == "MetalsOil":
        # First row = XAUUSD
        keyboard.append([InlineKeyboardButton("XAUUSD", callback_data="tech2_symbol_MetalsOil_XAUUSD")])
        # The rest: 2 per row
        remaining = instruments[1:]
        for i in range(0, len(remaining), 2):
            row = [InlineKeyboardButton(inst, callback_data=f"tech2_symbol_MetalsOil_{inst}") for inst in remaining[i:i+2]]
            keyboard.append(row)
    else:
        # 5 per row for Forex, Crypto, Index
        for i in range(0, len(instruments), 5):
            row = [InlineKeyboardButton(inst, callback_data=f"tech2_symbol_{category}_{inst}") for inst in instruments[i:i+5]]
            keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="ai_technical")])
    await query.message.edit_text(f"💹 *Select an Instrument from {category}:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# Step 3: Show Timeframes
async def show_timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, category, symbol = query.data.split("_", 2)

    keyboard = []
    for i in range(0, len(TIMEFRAMES), 3):
        row = [InlineKeyboardButton(tf, callback_data=f"tech2_chart_{symbol}_{tf}") for tf in TIMEFRAMES[i:i+3]]
        keyboard.append(row)

    # ✅ Back to instrument selection
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"tech2_cat_{category}")])
    await query.message.edit_text(f"🕒 *Select Timeframe for {symbol}:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


from io import BytesIO
import requests

async def fetch_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        parts = query.data.split("_")
        symbol = parts[-2]  # XRPUSDT
        tf = parts[-1]      # 5m

        full_symbol = f"BINANCE:{symbol}" if "USDT" in symbol else f"OANDA:{symbol}"
        payload = {"symbol": full_symbol, "interval": tf}

        print(f"🔍 Sending request to API with payload: {payload}")
        response = requests.post(API_URL, json=payload)
        print(f"📥 API response status: {response.status_code}")

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                image_bytes = BytesIO(response.content)
                await query.message.reply_photo(photo=image_bytes, caption=f"{symbol} ({tf}) Chart")
            else:
                print(f"❌ API returned non-image content: {response.text}")
                await query.message.reply_text("⚠️ Failed to fetch chart. Invalid response.")
        else:
            print(f"❌ API error response: {response.text}")
            await query.message.reply_text("⚠️ Failed to fetch chart. Please try again.")
    except Exception as e:
        print("❌ Exception while calling chart API:", e)
        await query.message.reply_text("❌ Server error. Try again later.")
