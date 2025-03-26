import httpx
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# Store live chat users
active_live_chat_users = set()

# Your deployed API endpoint
API_URL = "https://vessalivechat-production.up.railway.app/ask"

async def handle_live_chat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    active_live_chat_users.add(user_id)

    await query.message.edit_text(
        "🤖 You are now connected to VESSA Live Chat.\n\nAsk me anything below 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Exit", callback_data="live_chat_exit")]
        ])
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    user_msg = update.message.text

    if user_id not in active_live_chat_users:
        return

    print(f"🔥 USER IN LIVE CHAT: {user_id} - Message: {user_msg}")

    # Fetch answer from API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"question": user_msg})
            try:
                data = response.json()
            except Exception:
                data = {}
            answer = data.get("answer") or "🤖 Sorry, I don't understand that yet."
    except Exception as e:
        print(f"❌ Live chat API error: {e}")
        answer = "❌ Something went wrong. Please try again later."

    # Send answer
    try:
        user_message = update.message
        reply = await update.message.reply_text(answer)

        # Auto-delete user question and bot reply after 10 seconds
        await asyncio.sleep(10)
        await context.bot.delete_message(chat_id=user_message.chat_id, message_id=user_message.message_id)
        await context.bot.delete_message(chat_id=reply.chat_id, message_id=reply.message_id)
    except Exception as e:
        print(f"❌ Failed to send or delete message: {e}")
