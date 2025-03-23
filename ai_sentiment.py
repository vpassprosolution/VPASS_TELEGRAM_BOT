from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from utils import safe_replace_message
import httpx
import asyncio

# VPASS AI SENTIMENT API URL
VPASS_AI_SENTIMENT_URL = "https://vpassaisentiment-production.up.railway.app/storyline/?instrument="

# Correct Instrument Mapping (API-Compatible)
INSTRUMENTS = { 
    "gold": "gold",
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "dowjones": "dow-jones",
    "nasdaq": "nasdaq",
    "eur/usd": "eur-usd",
    "gbp/usd": "gbp-usd"
}

# Step 1: Show Instruments
async def show_instruments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("cooldown"):
        return
    context.user_data["cooldown"] = True
    asyncio.create_task(reset_cooldown(context))

    keyboard = [
        [InlineKeyboardButton("🏆 GOLD (XAUUSD)", callback_data="sentiment_gold")],
        [InlineKeyboardButton("₿ BITCOIN (BTC)", callback_data="sentiment_bitcoin"), InlineKeyboardButton("🔣 ETHEREUM (ETH)", callback_data="sentiment_ethereum")],
        [InlineKeyboardButton("📈 DOW JONES (DJI)", callback_data="sentiment_dowjones"), InlineKeyboardButton("📊 NASDAQ (IXIC)", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("💶 EUR/USD (EURUSD)", callback_data="sentiment_eur/usd"), InlineKeyboardButton("💷 GBP/USD (GBPUSD)", callback_data="sentiment_gbp/usd")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]
    ]

    if query.message.text and "CHOOSE YOUR STRATEGY" in query.message.text:
        await safe_replace_message(
            query,
            context,
            text="*Select Your Exclusive Instrument :*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="*Select Your Exclusive Instrument :*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# Step 2: Handle Instrument Selection
async def handle_instrument_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_instrument = query.data.replace("sentiment_", "")

    try:
        await query.edit_message_text(
            "🧠 *Fetching AI Sentiment... Please wait...*",
            parse_mode="Markdown"
        )
    except:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🧠 *Fetching AI Sentiment... Please wait...*",
            parse_mode="Markdown"
        )

    if selected_instrument in INSTRUMENTS:
        formatted_instrument = INSTRUMENTS[selected_instrument]
        api_url = f"{VPASS_AI_SENTIMENT_URL}{formatted_instrument}"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(api_url)
                if response.status_code == 200:
                    data = response.json().get("storyline", {})
                    storyline_text = data.get("storyline", "No sufficient data available.")
                    formatted_story = escape_markdown(storyline_text, version=2)
                    final_text = f"📌 *{selected_instrument.upper()} Sentiment Analysis*\n\n{formatted_story}"
                else:
                    final_text = f"⚠️ No sufficient data available for {selected_instrument.upper()}."
        except Exception as e:
            final_text = f"❌ Error fetching data: {escape_markdown(str(e), version=2)}"

        buttons = [
            [
                InlineKeyboardButton("🔁 Back to Instruments", callback_data="ai_sentiment"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]

        await safe_replace_message(
            query,
            context,
            text=final_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="MarkdownV2"
        )

# Cooldown reset function
async def reset_cooldown(context):
    await asyncio.sleep(1.5)
    context.user_data["cooldown"] = False
