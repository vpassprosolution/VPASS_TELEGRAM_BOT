import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import asyncio

API_SUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/subscribe"
API_UNSUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/unsubscribe"

INSTRUMENTS = ["GOLD", "BITCOIN", "ETHEREUM", "DOW JONES", "NASDAQ", "EUR/USD", "GBP/USD"]

async def reset_cooldown(context):
    await asyncio.sleep(1.5)
    context.user_data["cooldown"] = False

async def show_instruments(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("cooldown"):
        return
    context.user_data["cooldown"] = True
    asyncio.create_task(reset_cooldown(context))

    keyboard = [
        [InlineKeyboardButton("🏆 GOLD (XAUUSD)", callback_data="select_GOLD")],
        [InlineKeyboardButton("₿ BITCOIN (BTC)", callback_data="select_BITCOIN"), InlineKeyboardButton("🪙 ETHEREUM (ETH)", callback_data="select_ETHEREUM")],
        [InlineKeyboardButton("📈 DOW JONES (DJI)", callback_data="select_DOW JONES"), InlineKeyboardButton("📊 NASDAQ (IXIC)", callback_data="select_NASDAQ")],
        [InlineKeyboardButton("💶 EUR/USD (EURUSD)", callback_data="select_EUR/USD"), InlineKeyboardButton("💷 GBP/USD (GBPUSD)", callback_data="select_GBP/USD")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        "*Select Your Exclusive Instrument*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_subscription_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    instrument = query.data.replace("select_", "")

    keyboard = [
        [InlineKeyboardButton(f"✅ Subscribe to {instrument}", callback_data=f"subscribe_{instrument}"),
         InlineKeyboardButton(f"❌ Unsubscribe from {instrument}", callback_data=f"unsubscribe_{instrument}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_instruments")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        f"🔍 *{instrument} Subscription Menu:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def subscribe(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
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

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_instruments")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if success:
        await query.message.edit_text(f"✅ You are now subscribed to {instrument} alerts!", reply_markup=reply_markup)
    else:
        await query.message.edit_text(f"❌ Subscription failed for {instrument}. Try again.", reply_markup=reply_markup)

async def unsubscribe(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
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

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_instruments")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if success:
        await query.message.edit_text(f"🚫 You have unsubscribed from {instrument} alerts.", reply_markup=reply_markup)
    else:
        await query.message.edit_text(f"❌ Unsubscription failed for {instrument}. Try again.", reply_markup=reply_markup)

async def back_to_main(update: Update, context: CallbackContext) -> None:
    from bot import main_menu
    await main_menu(update, context)

async def back_to_instruments(update: Update, context: CallbackContext) -> None:
    await show_instruments(update, context)
