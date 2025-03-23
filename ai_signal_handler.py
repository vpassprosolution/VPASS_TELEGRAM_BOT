import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler
import asyncio

# AI API URL (Replace with your actual Railway URL)
AI_API_URL = "https://aiagentinstantsignal-production.up.railway.app"

# Cooldown reset
async def reset_cooldown(context):
    await asyncio.sleep(1.5)
    context.user_data["cooldown"] = False

# Function to fetch trade signal from the AI API
async def fetch_ai_signal(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("cooldown"):
        return
    context.user_data["cooldown"] = True
    asyncio.create_task(reset_cooldown(context))

    selected_instrument = query.data.replace("ai_signal_", "")
    if selected_instrument == "XAU":
        selected_instrument = "XAUUSD"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{AI_API_URL}/get_signal/{selected_instrument}")
            if response.status_code == 200:
                trade_signal = response.json().get("signal", "⚠️ No Signal Available")
            else:
                trade_signal = "⚠️ Error fetching signal"
    except Exception as e:
        print(f"❌ AI Signal Error: {e}")
        trade_signal = "❌ Unable to fetch signal at this time. Please try again later."

    formatted_message = f"⚡ *{selected_instrument}* Signal:\n{trade_signal}"
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ai_agent_signal")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        formatted_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Function to show instrument selection buttons
async def show_instruments(update, context):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("cooldown"):
        return
    context.user_data["cooldown"] = True
    asyncio.create_task(reset_cooldown(context))

    keyboard = [
        [InlineKeyboardButton("🏆 Gold", callback_data="ai_signal_XAUUSD")],
        [InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="ai_signal_BTC"), InlineKeyboardButton("🪙 ETHEREUM (ETH)", callback_data="ai_signal_ETH")],
        [InlineKeyboardButton("📊 Dow Jones (DJI)", callback_data="ai_signal_DJI"), InlineKeyboardButton("📊 NASDAQ (IXIC)", callback_data="ai_signal_IXIC")],
        [InlineKeyboardButton("💶 EUR/USD (EURUSD)", callback_data="ai_signal_EURUSD"), InlineKeyboardButton("💷 GBP/USD (GBPUSD)", callback_data="ai_signal_GBPUSD")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        "*Select Your Elite AI Insights*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Callback Query Handlers
ai_signal_handler = CallbackQueryHandler(fetch_ai_signal, pattern='^ai_signal_')
instrument_menu_handler = CallbackQueryHandler(show_instruments, pattern='^ai_agent_signal$')
