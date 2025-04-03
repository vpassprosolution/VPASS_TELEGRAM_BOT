import httpx
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from user_state import user_steps
from registration_handler import collect_user_data  # ✅ Add this clearly




# ✅ Set to track live chat users
active_live_chat_users = set()



# ✅ Your FastAPI endpoint
API_URL = "https://vessalivechat-production.up.railway.app/ask"


# ✅ When user enters Live Chat from setup
async def handle_live_chat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    active_live_chat_users.add(user_id)

    await query.message.edit_text(
        "🤖 You are now connected to VESSA Live Chat.\n\nAsk me anything below 👇\n\n"
        "❌ All chats auto-delete after 10 seconds.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Exit Live Chat", callback_data="live_chat_exit")]
        ])
    )


# ✅ When user sends a message during live chat
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    user_msg = update.message.text.strip()

    if user_id not in active_live_chat_users or not user_msg:
        return

    print(f"🔥 USER IN LIVE CHAT: {user_id} - Message: {user_msg}")

    # ✅ Call API to get best answer
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"question": user_msg})
            data = response.json()
            answer = data.get("answer") or "🤖 Sorry, I don't understand."
    except Exception as e:
        print(f"❌ Live chat API error: {e}")
        answer = "❌ Something went wrong. Please try again later."

    # ✅ Send bot reply
    try:
        reply = await update.message.reply_text(answer)
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")
        return

    # ✅ Auto-delete both messages after 10 seconds
    asyncio.create_task(delete_after_10s(context, update.message.chat_id, update.message.message_id))
    asyncio.create_task(delete_after_10s(context, reply.chat_id, reply.message_id))


# ✅ Delete message helper
async def delete_after_10s(context, chat_id, message_id):
    await asyncio.sleep(10)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass  # Ignore if already deleted

async def exit_live_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id in active_live_chat_users:
        active_live_chat_users.remove(user_id)

    # Go back to setup
    await query.message.edit_text(
        "🔙 Returned to SETUP MENU.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌐 Language", callback_data="language_menu"),
                InlineKeyboardButton("🎓 Tutorial", callback_data="coming_soon")
            ],
            [
                InlineKeyboardButton("💬 Live Chat", callback_data="live_chat"),
                InlineKeyboardButton("🛠️ Support", url="https://t.me/vpassprosupport")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
    )


async def route_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_steps:
        await collect_user_data(update, context)

    elif user_id in active_live_chat_users:
        await handle_user_message(update, context)

    else:
        # Optional fallback (ignore unknown text)
        pass
