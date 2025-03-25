import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler
import asyncio
from language_handler import get_text

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

    user_id = query.from_user.id
    get = lambda key: get_text(user_id, key, context)

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
        trade_signal = get("signal_error", context)

    formatted_message = f"Naomi Have *{selected_instrument}* Dicision\n{trade_signal}"
    keyboard = [[InlineKeyboardButton(get("btn_back", context), callback_data="ai_agent_signal")]]
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

    user_id = query.from_user.id
    get = lambda key: get_text(user_id, key, context)

    keyboard = [
        [InlineKeyboardButton(get("instrument_gold", context), callback_data="ai_signal_XAUUSD")],
        [
            InlineKeyboardButton(get("instrument_bitcoin", context), callback_data="ai_signal_BTC"),
            InlineKeyboardButton(get("instrument_ethereum", context), callback_data="ai_signal_ETH")
        ],
        [
            InlineKeyboardButton(get("instrument_dowjones", context), callback_data="ai_signal_DJI"),
            InlineKeyboardButton(get("instrument_nasdaq", context), callback_data="ai_signal_IXIC")
        ],
        [
            InlineKeyboardButton(get("instrument_eurusd", context), callback_data="ai_signal_EURUSD"),
            InlineKeyboardButton(get("instrument_gbpusd", context), callback_data="ai_signal_GBPUSD")
        ],
        [InlineKeyboardButton(get("btn_back", context), callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        get("smart_signal_title", context),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Callback Query Handlers
ai_signal_handler = CallbackQueryHandler(fetch_ai_signal, pattern='^ai_signal_')
instrument_menu_handler = CallbackQueryHandler(show_instruments, pattern='^ai_agent_signal$')
