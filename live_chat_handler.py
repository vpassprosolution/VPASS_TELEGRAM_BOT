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
    if not update.message or not update.message.text:
        return  # Skip if not a valid text message

    user_id = update.message.from_user.id
    user_msg = update.message.text

    if user_id not in active_live_chat_users:
        return  # Ignore messages not in live chat mode

    print(f"🔥 USER IN LIVE CHAT: {user_id} - Message: {user_msg}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"question": user_msg})
            raw = response.text
            print("✅ RAW API RESPONSE:", raw)

            data = response.json()
            answer = data.get("answer") or "🤖 No answer found in database."
    except Exception as e:
        print(f"❌ Live chat API error: {e}")
        answer = "❌ Sorry, something went wrong. Please try again later."

    # ✅ Send the answer to the user
    try:
        await update.message.reply_text(answer)
    except Exception as e:
        print(f"❌ Failed to reply in Telegram: {e}")

    # ✅ Auto-remove user from live chat session
    active_live_chat_users.remove(user_id)
    print(f"🔕 USER REMOVED FROM LIVE CHAT: {user_id}")
