import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import asyncio

# API URL for VPASS AI TECHNICAL
API_URL = "https://vpassaitechnical-production.up.railway.app/chart/"

async def show_technical_menu(update: Update, context: CallbackContext) -> None:
    """Show the instrument selection menu for AI Technical Analysis."""
    keyboard = [
        [InlineKeyboardButton("🥇 Gold (XAUUSD)", callback_data="instrument_gold")],
        [InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="instrument_bitcoin"),
         InlineKeyboardButton("Ξ Ethereum (ETH)", callback_data="instrument_ethereum")],
        [InlineKeyboardButton("📉 Dow Jones (DJI)", callback_data="instrument_dowjones"),
         InlineKeyboardButton("📈 Nasdaq (IXIC)", callback_data="instrument_nasdaq")],
        [InlineKeyboardButton("💱 EUR/USD (EURUSD)", callback_data="instrument_eurusd"),
         InlineKeyboardButton("💷 GBP/USD (GBPUSD)", callback_data="instrument_gbpusd")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("📊 **Select an Instrument for AI Technical Analysis**:", reply_markup=reply_markup)

async def show_timeframe_menu(update: Update, context: CallbackContext) -> None:
    """Show the timeframe selection menu after choosing an instrument."""
    query = update.callback_query
    instrument_map = {
        "instrument_gold": "Gold (XAUUSD)",
        "instrument_bitcoin": "Bitcoin (BTC)",
        "instrument_ethereum": "Ethereum (ETH)",
        "instrument_dowjones": "Dow Jones (DJI)",
        "instrument_nasdaq": "Nasdaq (IXIC)",
        "instrument_eurusd": "EUR/USD (EURUSD)",
        "instrument_gbpusd": "GBP/USD (GBPUSD)"
    }

    instrument_key = query.data
    if instrument_key not in instrument_map:
        await query.message.reply_text("❌ Invalid selection. Please try again.")
        return

    # Store selected instrument in user context
    context.user_data["selected_instrument"] = instrument_map[instrument_key]

    keyboard = [
        [InlineKeyboardButton("⏳ M5", callback_data="timeframe_5m"),
         InlineKeyboardButton("⏳ M15", callback_data="timeframe_15m"),
         InlineKeyboardButton("⏳ M30", callback_data="timeframe_30m")],
        [InlineKeyboardButton("⏳ H1", callback_data="timeframe_1h"),
         InlineKeyboardButton("⏳ H4", callback_data="timeframe_4h"),
         InlineKeyboardButton("⏳ Daily", callback_data="timeframe_1d")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_technical_instruments")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(f"📊 **Selected: {context.user_data['selected_instrument']}**\n\nNow choose a timeframe:", reply_markup=reply_markup)

import asyncio  # ✅ Ensure asyncio is imported

async def handle_technical_selection(update: Update, context: CallbackContext) -> None:
    """Handle timeframe selection and send chart."""
    query = update.callback_query

    # ✅ Ensure only one error message is visible at a time
    if "last_error_message_id" in context.user_data:
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data["last_error_message_id"])
        except:
            pass  # Ignore if already deleted

    if "selected_instrument" not in context.user_data:
        msg = await query.message.reply_text("❌ No instrument selected. Please go back and choose one.")
        context.user_data["last_error_message_id"] = msg.message_id  # ✅ Store message ID
        await asyncio.sleep(1)
        try:
            await msg.delete()
        except:
            pass  # Ignore errors if already deleted
        return

    instrument = context.user_data["selected_instrument"]
    timeframe_map = {
        "timeframe_5m": "5m",
        "timeframe_15m": "15m",
        "timeframe_30m": "30m",
        "timeframe_1h": "1h",
        "timeframe_4h": "4h",
        "timeframe_1d": "1d"
    }

    timeframe_key = query.data
    if timeframe_key not in timeframe_map:
        msg = await query.message.reply_text("❌ Failed to retrieve chart. Please try again.")
        context.user_data["last_error_message_id"] = msg.message_id  # ✅ Store message ID
        await asyncio.sleep(1)
        try:
            await msg.delete()
        except:
            pass  # Ignore errors if already deleted
        return

    timeframe = timeframe_map[timeframe_key]

    # Call the AI Technical API
    response = requests.get(API_URL, params={"instrument": instrument, "timeframe": timeframe})

    if response.status_code == 200:
        chart_url = response.json().get("chart_url")

        if chart_url:
            await query.message.reply_photo(photo=chart_url, caption=f"📊 {instrument} {timeframe.upper()} Chart")
        else:
            msg = await query.message.reply_text("❌ Failed to retrieve chart. Please try again.")
            context.user_data["last_error_message_id"] = msg.message_id  # ✅ Store message ID
            await asyncio.sleep(1)
            try:
                await msg.delete()
            except:
                pass  # Ignore errors if already deleted
    else:
        msg = await query.message.reply_text("❌ Error retrieving chart. Please try again.")
        context.user_data["last_error_message_id"] = msg.message_id  # ✅ Store message ID
        await asyncio.sleep(1)
        try:
            await msg.delete()
        except:
            pass  # Ignore errors if already deleted

async def back_to_instruments(update: Update, context: CallbackContext) -> None:
    """Back to instrument selection from timeframes."""
    await show_technical_menu(update, context)

async def back_to_main(update: Update, context: CallbackContext) -> None:
    """Back to main menu from instruments."""
    from bot import main_menu  # Import main menu function from bot.py
    await update.callback_query.message.edit_text("Welcome, Select Your Preference:", reply_markup=main_menu())
