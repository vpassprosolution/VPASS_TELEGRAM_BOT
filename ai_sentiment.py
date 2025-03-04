from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
import requests
import asyncio  # For smooth disappearing effect

# VPASS AI SENTIMENT API URL
VPASS_AI_SENTIMENT_URL = "https://vpassaisentiment-production.up.railway.app/storyline/?instrument="

# Correct Instrument Mapping (API requires '/' replaced with '-')
INSTRUMENTS = {
    "gold": "gold",
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "dow jones": "dow-jones",
    "nasdaq": "nasdaq",
    "eur/usd": "eur-usd",
    "gbp/usd": "gbp-usd"
}

async def delete_previous_message(update: Update):
    """Deletes the previous message with a smooth magic disappearing effect."""
    try:
        await asyncio.sleep(0.3)  # Small delay to enhance transition effect
        await update.callback_query.message.delete()
    except Exception:
        pass  # Ignore if message deletion fails

async def show_instruments(update: Update, context: CallbackContext):
    """Displays the 7-instrument menu after 'VPASS AI SENTIMENT' is clicked."""
    await delete_previous_message(update)  # Ensure previous menu disappears smoothly

    keyboard = [
        [InlineKeyboardButton("GOLD", callback_data="sentiment_gold")],
        [InlineKeyboardButton("BITCOIN", callback_data="sentiment_bitcoin"), InlineKeyboardButton("ETHEREUM", callback_data="sentiment_ethereum")],
        [InlineKeyboardButton("DOW JONES", callback_data="sentiment_dow jones"), InlineKeyboardButton("NASDAQ", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("EUR/USD", callback_data="sentiment_eur/usd"), InlineKeyboardButton("GBP/USD", callback_data="sentiment_gbp/usd")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]  # Back to VPASS AI SENTIMENT menu
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Select Your Preferred Instrument", reply_markup=reply_markup)

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument and fetches sentiment analysis text."""
    await delete_previous_message(update)  # Ensure previous menu disappears smoothly

    query = update.callback_query
    selected_instrument = query.data.replace("sentiment_", "")

    if selected_instrument in INSTRUMENTS:
        formatted_instrument = INSTRUMENTS[selected_instrument]
        api_url = f"{VPASS_AI_SENTIMENT_URL}{formatted_instrument}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                storyline_data = response.json().get("storyline", {})
                storyline_text = storyline_data.get("storyline", "No sufficient data available.")  
                formatted_storyline = escape_markdown(storyline_text, version=2)
                response_text = f"📌 *{selected_instrument.upper()} Sentiment Analysis*\n\n{formatted_storyline}"
            else:
                response_text = f"⚠️ No sufficient data available for {selected_instrument.upper()}."
        except Exception as e:
            response_text = f"❌ Error fetching data: {escape_markdown(str(e), version=2)}"

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="show_instruments")]]  # Correctly returns to 7-instrument menu as a new message
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.message.reply_text(response_text, parse_mode="MarkdownV2", reply_markup=reply_markup)
