import httpx
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from language_handler import get_text

API_SUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/subscribe"
API_UNSUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/unsubscribe"

async def reset_cooldown(context):
    await asyncio.sleep(1.5)
    context.user_data["cooldown"] = False

# ✅ Show instrument selection
async def show_instruments(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("cooldown"):
        return
    context.user_data["cooldown"] = True
    asyncio.create_task(reset_cooldown(context))

    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "instrument_gold", context), callback_data="select_GOLD")],
        [
            InlineKeyboardButton(get_text(user_id, "instrument_bitcoin", context), callback_data="select_BITCOIN"),
            InlineKeyboardButton(get_text(user_id, "instrument_ethereum", context), callback_data="select_ETHEREUM")
        ],
        [
            InlineKeyboardButton(get_text(user_id, "instrument_dowjones", context), callback_data="select_DOW JONES"),
            InlineKeyboardButton(get_text(user_id, "instrument_nasdaq", context), callback_data="select_NASDAQ")
        ],
        [
            InlineKeyboardButton(get_text(user_id, "instrument_eurusd", context), callback_data="select_EUR/USD"),
            InlineKeyboardButton(get_text(user_id, "instrument_gbpusd", context), callback_data="select_GBP/USD")
        ],
        [InlineKeyboardButton(get_text(user_id, "btn_back", context), callback_data="back_to_main")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        get_text(user_id, "smart_signal_title", context),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# ✅ Show subscribe/unsubscribe buttons
async def show_subscription_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    instrument = query.data.replace("select_", "")

    keyboard = [
        [
            InlineKeyboardButton(get_text(user_id, "subscribe_to", context).replace("{instrument}", instrument), callback_data=f"subscribe_{instrument}"),
            InlineKeyboardButton(get_text(user_id, "unsubscribe_from", context).replace("{instrument}", instrument), callback_data=f"unsubscribe_{instrument}")
        ],
        [InlineKeyboardButton(get_text(user_id, "btn_back", context), callback_data="back_to_instruments")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
    get_text(user_id, "subscription_menu_title", context).replace("{instrument}", instrument),
    reply_markup=reply_markup,
    parse_mode="Markdown"
)


# ✅ Subscribe user
async def subscribe(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    instrument = query.data.replace("subscribe_", "")
    chat_id = query.from_user.id

    payload = {"chat_id": chat_id, "instrument": instrument}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(API_SUBSCRIBE, json=payload)
            success = response.status_code == 200
    except Exception as e:
        print(f"❌ Subscribe Error: {e}")
        success = False

    keyboard = [[InlineKeyboardButton(get_text(user_id, "btn_back", context), callback_data="back_to_instruments")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if success:
        await query.message.edit_text(
            get_text(user_id, "sub_success", context).replace("{instrument}", instrument),
            reply_markup=reply_markup
        )
    else:
        await query.message.edit_text(
            get_text(user_id, "sub_failed", context).replace("{instrument}", instrument),
            reply_markup=reply_markup
        )

# ✅ Unsubscribe user
async def unsubscribe(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    instrument = query.data.replace("unsubscribe_", "")
    chat_id = query.from_user.id

    payload = {"chat_id": chat_id, "instrument": instrument}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(API_UNSUBSCRIBE, json=payload)
            success = response.status_code == 200
    except Exception as e:
        print(f"❌ Unsubscribe Error: {e}")
        success = False

    keyboard = [[InlineKeyboardButton(get_text(user_id, "btn_back", context), callback_data="back_to_instruments")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if success:
        await query.message.edit_text(
            get_text(user_id, "unsub_success", context).replace("{instrument}", instrument),
            reply_markup=reply_markup
        )
    else:
        await query.message.edit_text(
            get_text(user_id, "unsub_failed", context).replace("{instrument}", instrument),
            reply_markup=reply_markup
        )

# ✅ Back handlers
async def back_to_main(update: Update, context: CallbackContext) -> None:
    from bot import main_menu
    await main_menu(update, context)

async def back_to_instruments(update: Update, context: CallbackContext) -> None:
    await show_instruments(update, context)
