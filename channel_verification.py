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
    """Checks if the user has joined the Telegram channel AFTER email confirmation."""
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
                # ✅ User is a member → Proceed to next step
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

                            # ✅ Now the bot confirms registration is complete
                            return True  # ✅ User is a member, return True

                    except Exception as e:
                        print(f"❌ Database error: {e}")
                        conn.rollback()
                    finally:
                        conn.close()

            # ❌ User is NOT a member
            return False  

        else:
            print("❌ Failed to check membership. API Error.")
            return False  # ❌ Return False in case of an API failure

    except Exception as e:
        print(f"❌ Error checking Telegram membership: {e}")
        return False  # ❌ Return False in case of an exception



async def verify_active_membership(context: ContextTypes.DEFAULT_TYPE):
    """Checks if users are still in the channel and removes access if they left."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE is_member = TRUE;")
            users = cur.fetchall()

            for user in users:
                user_id = user[0]
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
                response = requests.get(url).json()

                if response.get("ok"):
                    status = response["result"]["status"]
                    if status not in ["member", "administrator", "creator"]:
                        # ❌ User left the channel → Remove access
                        cur.execute("UPDATE users SET is_member = FALSE WHERE user_id = %s;", (user_id,))
                        conn.commit()

                        # 🚨 Notify the user that they lost access
                        try:
                            await bot.send_message(
                                chat_id=user_id,
                                text="🚨 You left the VIP channel and lost access to VPASS PRO. Please rejoin to continue."
                            )
                        except Exception:
                            pass  # Ignore if user blocked the bot
                
                else:
                    print(f"Error checking membership for user {user_id}: {response}")  # Debugging info

                time.sleep(1)  # ✅ Add a 1-second delay to prevent API rate limits

            cur.close()
        except Exception as e:
            print(f"Error verifying membership: {e}")
        finally:
            conn.close()  # ✅ Ensure the connection is closed even if an error occurs
