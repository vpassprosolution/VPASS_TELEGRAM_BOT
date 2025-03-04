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
    """Displays the 7-instrument menu after 'VPASS AI SENTIMENT' is clicked."""
    query = update.callback_query

    # Edit message instead of deleting to apply instant replace effect
    keyboard = [
        [InlineKeyboardButton("GOLD", callback_data="sentiment_gold")],
        [InlineKeyboardButton("BITCOIN", callback_data="sentiment_bitcoin"), InlineKeyboardButton("ETHEREUM", callback_data="sentiment_ethereum")],
        [InlineKeyboardButton("DOW JONES", callback_data="sentiment_dow jones"), InlineKeyboardButton("NASDAQ", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("EUR/USD", callback_data="sentiment_eur/usd"), InlineKeyboardButton("GBP/USD", callback_data="sentiment_gbp/usd")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]  # Back to VPASS AI SENTIMENT menu
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Select Your Preferred Instrument", reply_markup=reply_markup)

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument and fetches sentiment analysis text."""
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

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="reset_main_menu")]]  # Correctly resets to main menu while keeping text
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(response_text, parse_mode="MarkdownV2", reply_markup=reply_markup)

async def reset_main_menu(update: Update, context: CallbackContext):
    """Resets the bot to the main menu as a fresh new message while keeping sentiment text."""
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("VPASS SMART SIGNAL", callback_data="smart_signal")],
        [InlineKeyboardButton("VPASS AI SENTIMENT", callback_data="ai_sentiment")],
        [
            InlineKeyboardButton("Forex Factory", url="https://www.forexfactory.com/"),
            InlineKeyboardButton("Discord", url="https://discord.com/"),
            InlineKeyboardButton("ChatGPT", url="https://chat.openai.com/"),
            InlineKeyboardButton("DeepSeek", url="https://www.deepseek.com/")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("Welcome, Select Your Preference", reply_markup=reply_markup)
