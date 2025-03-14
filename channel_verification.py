import requests
import asyncio
from db import connect_db
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import time  # ✅ Add this at the top

# Telegram Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"
CHANNEL_USERNAME = "vessacommunity"  # Your channel username without @

bot = Bot(token=BOT_TOKEN)

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE, user_steps):
    """Checks if the user has joined the Telegram channel before saving registration"""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id

    # ✅ Acknowledge button press only if it's a callback query
    if update.callback_query:
        await update.callback_query.answer()

    # ✅ Check membership using Telegram API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    
    try:
        response = requests.get(url).json()

        if response.get("ok"):
            status = response["result"]["status"]
            if status in ["member", "administrator", "creator"]:
                # ✅ User is a member → Save full registration in DB
                conn = connect_db()
                if conn:
                    try:
                        cur = conn.cursor()
                        if user_id in user_steps:  # Ensure user data exists
                            cur.execute(
                                """
                                INSERT INTO users (user_id, chat_id, name, username, contact, email, is_member)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (user_id) 
                                DO UPDATE SET chat_id = EXCLUDED.chat_id, 
                                              name = EXCLUDED.name, 
                                              username = EXCLUDED.username, 
                                              contact = EXCLUDED.contact, 
                                              email = EXCLUDED.email,
                                              is_member = TRUE;
                                """,
                                (user_id, chat_id, user_steps[user_id]["name"], user_steps[user_id]["username"],
                                 user_steps[user_id]["contact"], user_steps[user_id]["email"], True)
                            )
                            conn.commit()
                            cur.close()
                            conn.close()

                            # ✅ Show "Start VPASS PRO" button after successful verification
                            keyboard = [[InlineKeyboardButton("START VPASS PRO NOW", callback_data="start_vpass_pro")]]
                            reply_markup = InlineKeyboardMarkup(keyboard)

                            await update.message.reply_text(
                                "✅ Registration complete! You have successfully joined the channel!\n\n"
                                "Click below to start VPASS PRO:",
                                reply_markup=reply_markup
                            )

                            # ✅ Remove user tracking
                            del user_steps[user_id]
                        else:
                            await update.message.reply_text("❌ User data not found. Please restart registration.")

                    except Exception as e:
                        await update.message.reply_text(f"❌ Database error: {e}")
                        conn.rollback()
                    finally:
                        conn.close()

            else:
                # ❌ User is not a member - Show temporary warning and delete after 5 seconds
                warning_message = await update.message.reply_text(
                    "❌ You have NOT joined the channel!\n\n"
                    "🚨 Please **join here first:** [Join Here](https://t.me/vessacommunity)\n"
                    "Then click '✅ I Have Joined' again.",
                    parse_mode="Markdown"
                )

                # ✅ Delete the warning message after 5 seconds
                await asyncio.sleep(5)
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=warning_message.message_id)
                except Exception:
                    pass  # Ignore if message already deleted

        else:
            await update.message.reply_text("❌ Failed to check membership. Please try again later.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error checking Telegram membership: {e}")
