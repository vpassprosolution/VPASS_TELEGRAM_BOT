import requests
from db import connect_db
from telegram import Update
from telegram.ext import ContextTypes

# Telegram Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"
CHANNEL_USERNAME = "vessacommunity"  # Without '@'

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks if the user has joined the Telegram channel before saving registration"""
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    # ✅ Acknowledge button press
    await query.answer()

    # ✅ Check membership using Telegram API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    response = requests.get(url).json()

    if response.get("ok"):
        status = response["result"]["status"]
        if status in ["member", "administrator", "creator"]:
            # ✅ User is a member → Save registration in DB
            conn = connect_db()
            if conn:
                try:
                    cur = conn.cursor()
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
                except Exception as e:
                    await query.message.reply_text(f"❌ Error saving your data: {e}")

            # ✅ Show "Start VPASS PRO" button after successful verification
            keyboard = [[InlineKeyboardButton("START VPASS PRO NOW", callback_data="start_vpass_pro")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.edit_text(
                "✅ You have successfully joined the channel!\n\n"
                "Click below to start VPASS PRO:",
                reply_markup=reply_markup
            )

            # ✅ Remove user tracking
            del user_steps[user_id]

        else:
            # ❌ User is not a member
            await query.message.edit_text(
                "❌ You have NOT joined the channel yet.\n\n"
                "🚨 Please **join here first:** [Join Here](https://t.me/vessacommunity)\n"
                "Then click '✅ I Have Joined' again.",
                parse_mode="Markdown"
            )

    else:
        await query.message.reply_text("❌ Error checking Telegram membership. Please try again.")
