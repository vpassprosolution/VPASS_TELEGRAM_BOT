import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import connect_db
from menu import main_menu

async def reset_cooldown(context):
    await asyncio.sleep(1.5)
    context.user_data["cooldown"] = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("cooldown"):
        return
    context.user_data["cooldown"] = True
    asyncio.create_task(reset_cooldown(context))

    user_id = update.message.from_user.id

    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            username = user[0]
            try:
                welcome_video = "VP2.mp4"  # ✅ Use your video
                with open(welcome_video, "rb") as video:
                    await update.message.reply_video(video=video)
            except Exception as e:
                print(f"❌ Failed to send welcome video: {e}")

            keyboard = [[InlineKeyboardButton("Go to Main Menu", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Welcome back to world of AI {username}",
                reply_markup=reply_markup
            )
            return

    # ✅ If new user (not found in DB)
    try:
        welcome_video = "VP2.mp4"
        with open(welcome_video, "rb") as video:
            await update.message.reply_video(video=video)
    except Exception as e:
        print(f"❌ Failed to send welcome video: {e}")

    keyboard = [[InlineKeyboardButton("COMPLETE YOUR REGISTRATION", callback_data="register")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_message = await update.message.reply_text("WELCOME TO VESSA PRO VERSION 2.0", reply_markup=reply_markup)
    context.user_data["button_message"] = sent_message.message_id

async def start_vpass_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'START VPASS PRO NOW' button click"""
    query = update.callback_query
    await main_menu(update, context)
