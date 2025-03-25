from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import httpx
from io import BytesIO
import base64
from utils import safe_replace_message
import asyncio
from language_handler import get_text

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

async def reset_cooldown(context):
    await asyncio.sleep(1.5)
    context.user_data["cooldown"] = False

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("cooldown"):
        return
    context.user_data["cooldown"] = True
    asyncio.create_task(reset_cooldown(context))

    user_id = query.from_user.id
    get = lambda key: get_text(user_id, key, context)

    rows = []
    categories = list(INSTRUMENTS.keys())
    for i in range(0, len(categories), 2):
        row = [InlineKeyboardButton(get(f"category_{cat.lower()}"), callback_data=f"tech2_cat_{cat}") for cat in categories[i:i+2]]
        rows.append(row)

    rows.append([InlineKeyboardButton(get("btn_back"), callback_data="main_menu")])

    await safe_replace_message(
        query,
        context,
        text=get("technical_category_title"),
        reply_markup=InlineKeyboardMarkup(rows)
    )

async def show_technical_instruments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    get = lambda key: get_text(user_id, key, context)

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

    keyboard.append([InlineKeyboardButton(get("btn_back"), callback_data="ai_technical")])

    await safe_replace_message(
        query,
        context,
        text=get("technical_instrument_title").replace("{category}", category),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    get = lambda key: get_text(user_id, key, context)

    _, category, symbol = query.data.split("_", 2)

    # ✅ Load translated labels from your dict
    lang = context.user_data.get("user_lang", "en")
    labels = get_text(user_id, "timeframe_labels", context)

    keyboard = []
    for i in range(0, len(TIMEFRAMES), 3):
        row = [
            InlineKeyboardButton(labels.get(tf, tf), callback_data=f"tech2_chart_{category}_{symbol}_{tf}")
            for tf in TIMEFRAMES[i:i+3]
        ]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(get("btn_back"), callback_data=f"tech2_cat_{category}")])

    try:
        await query.edit_message_text(
            text=get("technical_timeframe_title").replace("{symbol}", symbol),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"🕒 *Select Timeframe for {symbol}:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def fetch_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass

    try:
        parts = query.data.split("_")
        category = parts[-3]
        symbol = parts[-2]
        tf = parts[-1]

        loading_message = await query.edit_message_text(
            "⏳ *Analyzing chart... Please wait...*",
            parse_mode="Markdown"
        )

        if category == "Crypto":
            full_symbol = f"BINANCE:{symbol}"
        elif category == "Index":
            full_symbol = f"TVC:{symbol}"
        elif category == "MetalsOil":
            full_symbol = "TVC:USOIL" if symbol == "WTI" else f"OANDA:{symbol}"
        else:
            full_symbol = f"OANDA:{symbol}"

        payload = {"symbol": full_symbol, "interval": tf}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(API_URL, json=payload)
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

                    # ✅ TRANSLATION
                    user_id = query.from_user.id
                    get = lambda key: get_text(user_id, key, context)

                    footer_buttons = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(get("chart_back_timeframe"), callback_data=f"tech2_symbol_{category}_{symbol}"),
                            InlineKeyboardButton(get("chart_back_menu"), callback_data="main_menu")
                        ]
                    ])

                    await context.bot.send_photo(
                        chat_id=query.message.chat.id,
                        photo=image_stream,
                        caption=data["caption"],
                        reply_markup=footer_buttons
                    )
                else:
                    await query.message.reply_text("⚠️ Incomplete chart data. Please try again.")
            else:
                await query.message.reply_text("⚠️ Chart fetch failed. Try again.")
    except Exception as e:
        print(f"❌ Exception: {e}")
        await query.message.reply_text("❌ Server error. Please try again.")
