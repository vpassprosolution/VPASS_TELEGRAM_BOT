import httpx
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
    user_msg = update.message.text

    if user_id not in active_live_chat_users:
        return  # User not in live chat mode

    print(f"🔥 USER IN LIVE CHAT: {user_id} - Message: {user_msg}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"question": user_msg})
            raw = response.text
            print("✅ RAW API RESPONSE:", raw)

            data = response.json()
            answer = data.get("answer")

            if not answer or answer.strip() == "":
                answer = "🤖 Sorry, I don't have an answer for that yet. We're always learning!"
    except Exception as e:
        print(f"❌ Live chat API error: {e}")
        answer = "❌ Sorry, something went wrong while getting a reply."

    # ✅ Create inline buttons
    keyboard = [
        [
            InlineKeyboardButton("❌ Exit", callback_data="live_chat_exit"),
            InlineKeyboardButton("➡️ Ask Another", callback_data="live_chat_continue")
        ]
    ]

    # ✅ Send the answer + buttons
    try:
        await update.message.reply_text(answer, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(f"❌ Failed to send message in Telegram: {e}")
