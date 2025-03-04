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
    """Displays the list of instruments when 'VPASS AI SENTIMENT' is clicked."""
    query = update.callback_query

    # Arrange instruments in the requested layout
    keyboard = [
        [InlineKeyboardButton("GOLD", callback_data="sentiment_gold")],
        [InlineKeyboardButton("BITCOIN", callback_data="sentiment_bitcoin"), InlineKeyboardButton("ETHEREUM", callback_data="sentiment_ethereum")],
        [InlineKeyboardButton("DOW JONES", callback_data="sentiment_dow jones"), InlineKeyboardButton("NASDAQ", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("EUR/USD", callback_data="sentiment_eur/usd"), InlineKeyboardButton("GBP/USD", callback_data="sentiment_gbp/usd")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send instrument selection message
    await query.message.reply_text("Select Your Preferred Instrument", reply_markup=reply_markup)

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument."""
    query = update.callback_query
    selected_instrument = query.data.replace("sentiment_", "")

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

        # Show sentiment text with buttons below
        keyboard = [
            [InlineKeyboardButton("🔙 Menu", callback_data="return_to_instruments")],  # Brings back 7-instrument menu
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]  # Back to main menu
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(response_text, parse_mode="MarkdownV2", reply_markup=reply_markup)

async def return_to_instruments(update: Update, context: CallbackContext):
    """Brings back the 7-instrument menu while keeping sentiment text visible."""
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("GOLD", callback_data="sentiment_gold")],
        [InlineKeyboardButton("BITCOIN", callback_data="sentiment_bitcoin"), InlineKeyboardButton("ETHEREUM", callback_data="sentiment_ethereum")],
        [InlineKeyboardButton("DOW JONES", callback_data="sentiment_dow jones"), InlineKeyboardButton("NASDAQ", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("EUR/USD", callback_data="sentiment_eur/usd"), InlineKeyboardButton("GBP/USD", callback_data="sentiment_gbp/usd")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("Select Your Preferred Instrument", reply_markup=reply_markup)
