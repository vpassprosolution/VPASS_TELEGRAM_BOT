from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
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

    # Create buttons for the instruments
    keyboard = [[InlineKeyboardButton(inst.upper(), callback_data=f"sentiment_{inst}")] for inst in INSTRUMENTS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit the message to show the instrument options
    await query.message.edit_text("Select an instrument:", reply_markup=reply_markup)

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument."""
    query = update.callback_query
    selected_instrument = query.data.replace("sentiment_", "")  # Extract the instrument name

    if selected_instrument in INSTRUMENTS:
        formatted_instrument = INSTRUMENTS[selected_instrument]  # Get API-compatible format
        api_url = f"{VPASS_AI_SENTIMENT_URL}{formatted_instrument}"

        # Send request to API
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                storyline = response.json().get("storyline", "No sufficient data available.")

if isinstance(storyline, list):  # If API returns a list of events
    formatted_storyline = "\n".join([f"📍 {event}" for event in storyline])
else:
    formatted_storyline = storyline

response_text = (
    f"📌 **{selected_instrument.upper()} Sentiment Analysis**\n\n"
    f"📢 {formatted_storyline}\n\n"
    "📊 **Key Insights:**\n"
    "🏦 **Central Banks Are Buying:** Increased reserves show lack of trust in fiat currencies.\n"
    "📉 **Stock Market Uncertainty:** Traders seek gold as a safe haven.\n"
    "🌎 **Geopolitical Tensions:** Global conflicts drive demand for gold.\n\n"
    "🔎 **What to Watch:**\n"
    "➡️ If gold breaks above a key resistance level, expect further rallies.\n"
    "⬇️ A drop below support levels may signal a correction.\n\n"
    "💡 **Final Verdict:** Stay alert for opportunities!"
)

                response_text = f"📊 **{selected_instrument.upper()} Storyline:**\n\n{storyline}"
            else:
                response_text = f"⚠️ No sufficient data available for {selected_instrument.upper()}."
        except Exception as e:
            response_text = f"❌ Error fetching data: {str(e)}"

        await query.message.edit_text(response_text)
