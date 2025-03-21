from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import requests
from io import BytesIO
import base64

API_URL = "https://aitechnical-production.up.railway.app/get_chart_image"

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

    await query.edit_message_text(
        text="📊 *Select a Market Category:*",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )

# Step 2: Show Instruments
async def show_technical_instruments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("tech2_cat_", "")
    instruments = INSTRUMENTS.get(category, [])

    keyboard = []

    if category == "MetalsOil":
        keyboard.append([InlineKeyboardButton("XAUUSD", callback_data="tech2_symbol_MetalsOil_XAUUSD")])
        remaining = instruments[1:]
        for i in range(0, len(remaining), 2):
            row = [InlineKeyboardButton(inst, callback_data=f"tech2_symbol_MetalsOil_{inst}") for inst in remaining[i:i+2]]
            keyboard.append(row)
    else:
        for i in range(0, len(instruments), 5):
            row = [InlineKeyboardButton(inst, callback_data=f"tech2_symbol_{category}_{inst}") for inst in instruments[i:i+5]]
            keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="ai_technical")])

    await query.edit_message_text(
        text=f"💹 *Select an Instrument from {category}:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Step 3: Show Timeframes
async def show_timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, category, symbol = query.data.split("_", 2)

    keyboard = []
    for i in range(0, len(TIMEFRAMES), 3):
        row = [
            InlineKeyboardButton(tf, callback_data=f"tech2_chart_{category}_{symbol}_{tf}")
            for tf in TIMEFRAMES[i:i+3]
        ]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"tech2_cat_{category}")])

    try:
        await query.edit_message_text(
            text=f"🕒 *Select Timeframe for {symbol}:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception:
        # If previous message is a photo → fallback
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"🕒 *Select Timeframe for {symbol}:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


# Step 4: Fetch Chart from API
async def fetch_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print("⚠️ Skipped query.answer():", e)

    try:
        parts = query.data.split("_")
        category = parts[-3]
        symbol = parts[-2]
        tf = parts[-1]

        # Show loading message
        loading_message = await query.edit_message_text(
            "⏳ *Analyzing chart... Please wait...*",
            parse_mode="Markdown"
        )

        # ✅ Symbol prefix logic
        if category == "Crypto":
            full_symbol = f"BINANCE:{symbol}"
        elif category == "Index":
            full_symbol = f"TVC:{symbol}"
        elif category == "MetalsOil":
            if symbol == "WTI":
                full_symbol = "TVC:USOIL"
            else:
                full_symbol = f"OANDA:{symbol}"  # ✅ Use OANDA for XAUUSD, XAGUSD, etc.
        else:
            full_symbol = f"OANDA:{symbol}"

        payload = {"symbol": full_symbol, "interval": tf}

        print(f"🔍 Sending request to API with payload: {payload}")
        response = requests.post(API_URL, json=payload)
        print(f"📥 API response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if "image_base64" in data and "caption" in data:
                await context.bot.delete_message(
                    chat_id=query.message.chat.id,
                    message_id=loading_message.message_id
                )

                image_data = base64.b64decode(data["image_base64"])
                image_stream = BytesIO(image_data)
                image_stream.name = "chart.png"
                image_stream.seek(0)

                footer_buttons = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔁 Back to Timeframe", callback_data=f"tech2_symbol_{category}_{symbol}"),
                        InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
                    ]
                ])

                await context.bot.send_photo(
                    chat_id=query.message.chat.id,
                    photo=image_stream,
                    caption=data["caption"],
                    reply_markup=footer_buttons
                )
            else:
                print(f"❌ API missing keys: {data}")
                await query.message.reply_text("⚠️ Incomplete chart data. Please try again.")
        else:
            print(f"❌ API error: {response.text}")
            await query.message.reply_text("⚠️ Chart fetch failed. Try again.")
    except Exception as e:
        print(f"❌ Exception: {e}")
        await query.message.reply_text("❌ Server error. Please try again.")