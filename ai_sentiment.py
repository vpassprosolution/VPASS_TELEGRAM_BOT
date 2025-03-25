from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from utils import safe_replace_message
import httpx
import asyncio
from language_handler import get_text

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

    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "instrument_gold", context), callback_data="sentiment_gold")],
        [
            InlineKeyboardButton(get_text(user_id, "instrument_bitcoin", context), callback_data="sentiment_bitcoin"),
            InlineKeyboardButton(get_text(user_id, "instrument_ethereum", context), callback_data="sentiment_ethereum")
        ],
        [
            InlineKeyboardButton(get_text(user_id, "instrument_dowjones", context), callback_data="sentiment_dowjones"),
            InlineKeyboardButton(get_text(user_id, "instrument_nasdaq", context), callback_data="sentiment_nasdaq")
        ],
        [
            InlineKeyboardButton(get_text(user_id, "instrument_eurusd", context), callback_data="sentiment_eur/usd"),
            InlineKeyboardButton(get_text(user_id, "instrument_gbpusd", context), callback_data="sentiment_gbp/usd")
        ],
        [InlineKeyboardButton(get_text(user_id, "sentiment_back", context), callback_data="main_menu")]
    ]

    await query.message.edit_text(
        get_text(user_id, "sentiment_title", context),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# Step 2: Handle Instrument Selection
async def handle_instrument_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    selected_instrument = query.data.replace("sentiment_", "")

    try:
        await query.edit_message_text(
            get_text(user_id, "sentiment_loading", context),
            parse_mode="Markdown"
        )
    except:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=get_text(user_id, "sentiment_loading", context),
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
                InlineKeyboardButton(get_text(user_id, "sentiment_back_instruments", context), callback_data="ai_sentiment"),
                InlineKeyboardButton(get_text(user_id, "sentiment_back_menu", context), callback_data="main_menu")
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
