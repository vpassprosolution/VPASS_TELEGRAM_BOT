import httpx
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# Store live chat users
active_live_chat_users = set()

API_URL = "https://vessalivechat-production.up.railway.app/ask"

async def handle_live_chat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    active_live_chat_users.add(user_id)

    await query.message.edit_text(
        "🤖 You are now connected to VESSA Live Chat.\n\nAsk me anything below 👇"
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    user_msg = update.message.text

    if user_id not in active_live_chat_users:
        return

    print(f"🔥 USER IN LIVE CHAT: {user_id} - Message: {user_msg}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"question": user_msg})
            data = response.json()
            answer = data.get("answer", "🤖 Sorry, I don't understand.")
    except Exception as e:
        print(f"❌ Live chat API error: {e}")
        answer = "❌ Something went wrong. Please try again later."

    # ✅ Send reply with inline buttons
    reply = await update.message.reply_text(
        answer,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("❌ Exit", callback_data="live_chat_exit"),
                InlineKeyboardButton("➡️ Ask Another", callback_data="live_chat_continue")
            ]
        ])
    )

    # ✅ Auto-delete both after 10 seconds
    await asyncio.sleep(10)
    try:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        await context.bot.delete_message(chat_id=reply.chat_id, message_id=reply.message_id)
    except:
        pass
