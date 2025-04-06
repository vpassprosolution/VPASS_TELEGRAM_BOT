from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import httpx
from utils import safe_replace_message  # ✅ Using stable version with context
import html

# ✅ Category Maps
category_map = {
    "sentiment_metals": "Metals",
    "sentiment_forex": "Forex",
    "sentiment_crypto": "Crypto",
    "sentiment_index": "Index"
}

# ✅ Instrument Maps
instrument_map = {
    "sentiment_metals": {
        "XAU": "Gold", "XAG": "Silver", "XCU": "Copper", "XPT": "Platinum", "XPD": "Palladium",
        "ALU": "Aluminum", "ZNC": "Zinc", "NI": "Nickel", "TIN": "Tin", "LEAD": "Lead"
    },
    "sentiment_forex": {
        "EURUSD": "EUR/USD", "GBPUSD": "GBP/USD", "AUDUSD": "AUD/USD", "NZDUSD": "NZD/USD", "USDJPY": "USD/JPY",
        "USDCAD": "USD/CAD", "USDCHF": "USD/CHF", "USDCNH": "USD/CNH", "USDHKD": "USD/HKD", "USDSEK": "USD/SEK",
        "USDSGD": "USD/SGD", "USDNOK": "USD/NOK", "USDMXN": "USD/MXN", "USDZAR": "USD/ZAR", "USDTHB": "USD/THB",
        "USDKRW": "USD/KRW", "USDPHP": "USD/PHP", "USDTRY": "USD/TRY", "USDINR": "USD/INR", "USDVND": "USD/VND"
    },
    "sentiment_crypto": {
        "BTCUSD": "Bitcoin", "ETHUSD": "Ethereum", "BNBUSD": "BNB", "XRPUSD": "XRP", "ADAUSD": "ADA",
        "SOLUSD": "Solana", "DOGEUSD": "DOGE", "TRXUSD": "TRX", "DOTUSD": "DOT", "AVAXUSD": "AVAX",
        "SHIBUSD": "SHIBA", "MATICUSD": "MATIC", "LTCUSD": "Litecoin", "BCHUSD": "BCH", "UNIUSD": "Uniswap",
        "LINKUSD": "Chainlink", "XLMUSD": "Stellar", "ATOMUSD": "Cosmos", "ETCUSD": "ETC", "XMRUSD": "Monero"
    },
    "sentiment_index": {
        "DJI": "Dow Jones", "IXIC": "Nasdaq", "GSPC": "S&P 500", "FTSE": "FTSE 100", "N225": "Nikkei 225",
        "HSI": "Hang Seng", "DAX": "DAX", "CAC40": "CAC 40", "STOXX50": "Euro Stoxx 50", "AORD": "ASX 200",
        "BSESN": "Sensex", "NSEI": "Nifty 50", "KS11": "KOSPI", "TWII": "Taiwan Index", "BVSP": "Bovespa",
        "MXX": "IPC Mexico", "RUT": "Russell 2000", "VIX": "Volatility", "XU100": "BIST 100"
    }
}

# ✅ Show Sentiment Categories
async def show_sentiment_categories(update, context):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🟨 Metals", callback_data="sentiment_metals"),
         InlineKeyboardButton("🟦 Forex", callback_data="sentiment_forex")],
        [InlineKeyboardButton("🟩 Crypto", callback_data="sentiment_crypto"),
         InlineKeyboardButton("🟥 Index", callback_data="sentiment_index")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]
    ]
    await safe_replace_message(query, context, "📊 Choose a sentiment category:", InlineKeyboardMarkup(keyboard))


# ✅ Show Instruments
async def show_sentiment_instruments(update, context):
    query = update.callback_query
    category = query.data
    instruments = instrument_map[category]

    keyboard = []
    row = []
    for idx, (symbol, label) in enumerate(instruments.items(), start=1):
        row.append(InlineKeyboardButton(label, callback_data=f"get_sentiment|{category}|{symbol}"))
        if idx % 5 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("⬅️ Back to Category", callback_data="vessa_ai_sentiment")])

    await safe_replace_message(query, context, "📈 Choose an instrument:", InlineKeyboardMarkup(keyboard))


# ✅ Get Sentiment from API
async def fetch_sentiment(update, context):
    query = update.callback_query
    _, category, symbol = query.data.split("|")
    await safe_replace_message(query, context, "🧠 Generating AI Sentiment...")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            url = f"https://vessaaisentimentapi-production.up.railway.app/sentiment/metals?symbol={symbol}" if category == "sentiment_metals" else \
                  f"https://vessaaisentimentapi-production.up.railway.app/sentiment/others?symbol={symbol}"

            res = await client.get(url)
            data = res.json()

        if "sentiment" in data:
            keyboard = [[InlineKeyboardButton("⬅️ Back to Category", callback_data=category)]]
            await query.message.edit_text(
                data["sentiment"],
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.message.edit_text("⚠️ Failed to get sentiment data.")

    except Exception as e:
        await query.message.edit_text(f"❌ Error fetching sentiment: {e}")
