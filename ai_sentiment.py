from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
import requests

# VPASS AI SENTIMENT API URL
VPASS_AI_SENTIMENT_URL = "https://vpassaisentiment-production.up.railway.app/storyline/?instrument="

# Correct Instrument Mapping (Follow API Formatting)
INSTRUMENTS = { 
    "gold": "gold",
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "dowjones": "dow-jones",  # Fixed: Now matches API format
    "nasdaq": "nasdaq",
    "eur/usd": "eur-usd",  # Fixed: Now matches API format
    "gbp/usd": "gbp-usd"   # Fixed: Now matches API format
}

async def show_instruments(update: Update, context: CallbackContext):
    """Displays the list of instruments when 'VPASS AI SENTIMENT' is clicked or when returning from sentiment analysis."""
    query = update.callback_query

    # Arrange instruments in the requested layout
    keyboard = [
        [InlineKeyboardButton("🏆 GOLD (XAUUSD)", callback_data="sentiment_gold")],
        [InlineKeyboardButton("₿ BITCOIN (BTC)", callback_data="sentiment_bitcoin"), InlineKeyboardButton("🟣 ETHEREUM (ETH)", callback_data="sentiment_ethereum")],
        [InlineKeyboardButton("📈 DOW JONES (DJI)", callback_data="sentiment_dowjones"), InlineKeyboardButton("📊 NASDAQ (IXIC)", callback_data="sentiment_nasdaq")],
        [InlineKeyboardButton("💶 EUR/USD (EURUSD)", callback_data="sentiment_eur/usd"), InlineKeyboardButton("💷 GBP/USD (GBPUSD)", callback_data="sentiment_gbp/usd")],  
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("Select our exclusive range of instruments", reply_markup=reply_markup)

async def handle_instrument_selection(update: Update, context: CallbackContext):
    """Handles when a user selects an instrument."""
    query = update.callback_query
    selected_instrument = query.data.replace("sentiment_", "")  # Extract the instrument name

    # Show fetching message
    fetching_message = await query.message.reply_text("Fetching sentiment analysis...")

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

        # Button: Back to Instruments + Main Menu
        keyboard = [
            [
                InlineKeyboardButton("🔁 Back to Instruments", callback_data="ai_sentiment"),
                InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=query.message.chat_id, text=response_text, parse_mode="MarkdownV2", reply_markup=reply_markup)
