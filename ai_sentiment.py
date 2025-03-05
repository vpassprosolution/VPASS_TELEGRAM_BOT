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
    "dowjones": "dowjones",
    "nasdaq": "nasdaq",
    "eur/usd": "eur-usd",
    "gbp/usd": "gbp-usd"
}

async def show_instruments(update: Update, context: CallbackContext):
    """Displays the list of instruments when 'VPASS AI SENTIMENT' is clicked or when returning from sentiment analysis."""
    query = update.callback_query

    # Delete the previous message (to remove buttons)
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception:
        pass  # Ignore if deletion fails

    # Arrange instruments in the requested layout
    keyboard = [
        [InlineKeyboardButton("GOLD", callback_data="sentiment_gold")],  # Gold at the top
        [InlineKeyboardButton("BITCOIN", callback_data="sentiment_bitcoin"), InlineKeyboardButton("ETHEREUM", callback_data="sentiment_ethereum")],  # Side by side
        [InlineKeyboardButton("DOW JONES", callback_data="sentiment_dowjones"), InlineKeyboardButton("NASDAQ", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("EUR/USD", callback_data="sentiment_eur-usd"), InlineKeyboardButton("GBP/USD", callback_data="sentiment_gbp-usd")],  # Fixed callback data
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]  # Back button to main menu
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a NEW menu message and store its message_id
    sent_message = await query.message.reply_text("Select our exclusive range of instruments", reply_markup=reply_markup)
    context.user_data["instrument_menu_message_id"] = sent_message.message_id  # Store message ID

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument."""
    query = update.callback_query
    selected_instrument = query.data.replace("sentiment_", "")  # Extract the instrument name

    # Delete the instrument menu message (so the selection disappears)
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data["instrument_menu_message_id"])
    except Exception:
        pass  

    # Show fetching message
    fetching_message = await query.message.reply_text("Fetching sentiment analysis...")

    if selected_instrument in INSTRUMENTS:
        formatted_instrument = INSTRUMENTS[selected_instrument]  # Get API-compatible format
        api_url = f"{VPASS_AI_SENTIMENT_URL}{formatted_instrument}"

        # Send request to API
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                # Extract the nested storyline text from the API response
                storyline_data = response.json().get("storyline", {})  
                storyline_text = storyline_data.get("storyline", "No sufficient data available.")  

                # Escape special characters for Telegram Markdown V2
                formatted_storyline = escape_markdown(storyline_text, version=2)

                response_text = f"📌 *{selected_instrument.upper()} Sentiment Analysis*\n\n{formatted_storyline}"
            else:
                response_text = f"⚠️ No sufficient data available for {selected_instrument.upper()}."
        except Exception as e:
            response_text = f"❌ Error fetching data: {escape_markdown(str(e), version=2)}"

        # Delete the "Fetching sentiment analysis..." message
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=fetching_message.message_id)
        except Exception:
            pass  # Ignore errors if message doesn't exist

        # Add "Menu" button BELOW the sentiment text (so sentiment text stays)
        keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="ai_sentiment")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(response_text, parse_mode="MarkdownV2", reply_markup=reply_markup)
