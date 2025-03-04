from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import requests

# VPASS AI SENTIMENT API URL
VPASS_AI_SENTIMENT_URL = "https://vpassaisentiment-production.up.railway.app"

# Define the available instruments
INSTRUMENTS = {
    "gold": "gold",
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "dow jones": "dow jones",
    "nasdaq": "nasdaq",
    "eur/usd": "eur/usd",
    "gbp/usd": "gbp/usd"
}

async def show_instruments(update: Update, context: CallbackContext):
    """Displays the list of 7 instruments when 'VPASS AI SENTIMENT' is clicked."""
    query = update.callback_query

    # Create buttons for the 7 instruments
    keyboard = [[InlineKeyboardButton(inst, callback_data=f"sentiment_{inst.lower()}")] for inst in INSTRUMENTS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit the message to show the instrument options
    await query.message.edit_text("Select an instrument:", reply_markup=reply_markup)

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument."""
    query = update.callback_query
    selected_instrument = query.data.replace("sentiment_", "").upper()  # Extract the instrument name

    if selected_instrument in INSTRUMENTS:
        if selected_instrument == "GOLD":
            # Redirect to VPASS_AI_SENTIMENT API
            response_text = f"You selected {selected_instrument}. Redirecting to VPASS AI SENTIMENT..."
            ai_sentiment_url = f"{VPASS_AI_SENTIMENT_URL}/{INSTRUMENTS[selected_instrument]}"
            requests.get(ai_sentiment_url)  # This makes a request to the external project
        else:
            response_text = f"You selected {selected_instrument}. Processing data..."

        await query.message.edit_text(response_text)
