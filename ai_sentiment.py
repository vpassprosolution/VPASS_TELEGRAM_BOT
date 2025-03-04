from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
import requests

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

async def show_instruments(update: Update, context: CallbackContext):
    """Displays the list of instruments when 'VPASS AI SENTIMENT' is clicked or when returning from sentiment analysis."""
    query = update.callback_query

    # Delete the previous menu message
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception:
        pass  # Ignore if deletion fails

    # Arrange instruments in the requested layout
    keyboard = [
        [InlineKeyboardButton("GOLD", callback_data="sentiment_gold")],
        [InlineKeyboardButton("BITCOIN", callback_data="sentiment_bitcoin"), InlineKeyboardButton("ETHEREUM", callback_data="sentiment_ethereum")],
        [InlineKeyboardButton("DOW JONES", callback_data="sentiment_dow jones"), InlineKeyboardButton("NASDAQ", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("EUR/USD", callback_data="sentiment_eur/usd"), InlineKeyboardButton("GBP/USD", callback_data="sentiment_gbp/usd")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]  # Back to main menu
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the instrument selection menu
    await query.message.reply_text("Select Your Preferred Instrument", reply_markup=reply_markup)

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument and fetches sentiment analysis text."""
    query = update.callback_query
    selected_instrument = query.data.replace("sentiment_", "")

    # Delete the previous 7-instrument menu
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception:
        pass  # Ignore if deletion fails

    if selected_instrument in INSTRUMENTS:
        formatted_instrument = INSTRUMENTS[selected_instrument]
        api_url = f"{VPASS_AI_SENTIMENT_URL}{formatted_instrument}"

        # Fetch sentiment analysis data
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

        # Show sentiment text with "Back" button below it (calls show_instruments())
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="show_instruments")]]  # Returns to 7-instrument menu
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(response_text, parse_mode="MarkdownV2", reply_markup=reply_markup)
