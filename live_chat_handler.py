import httpx
from telegram import Update
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
    user_id = update.message.from_user.id

    if user_id not in active_live_chat_users:
        return  # Ignore messages not in live chat mode

    user_msg = update.message.text

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"question": user_msg})
            data = response.json()
            answer = data.get("answer", "🤖 Sorry, something went wrong.")
    except Exception as e:
        print(f"❌ Live chat API error: {e}")
        answer = "❌ Failed to get a reply from VESSA Live Chat."

    await update.message.reply_text(answer)
