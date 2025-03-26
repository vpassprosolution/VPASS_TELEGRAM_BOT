import httpx
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Track live chat state per user
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
    chat_id = update.message.chat_id
    user_msg = update.message.text

    if user_id not in active_live_chat_users:
        return

    print(f"🔥 USER IN LIVE CHAT: {user_id} - Message: {user_msg}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"question": user_msg})
            raw = response.text
            print("✅ RAW API RESPONSE:", raw)
            data = response.json()
            answer = data.get("answer") or "🤖 Sorry, I don't understand that."
    except Exception as e:
        print(f"❌ Live chat API error: {e}")
        answer = "❌ Something went wrong. Please try again later."

    # ✅ Send the bot's reply with Exit & Ask Another buttons
    keyboard = [
        [
            InlineKeyboardButton("❌ Exit", callback_data="live_chat_exit"),
            InlineKeyboardButton("➡️ Ask Another", callback_data="live_chat_continue")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # ✅ Save the user message and bot message
    try:
        bot_reply = await update.message.reply_text(answer, reply_markup=reply_markup)
    except Exception as e:
        print(f"❌ Failed to send bot reply: {e}")
        return

    # ✅ Auto-delete after 5 seconds
    await asyncio.sleep(5)

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        await context.bot.delete_message(chat_id=chat_id, message_id=bot_reply.message_id)
    except Exception as e:
        print(f"❌ Error deleting messages: {e}")
