import requests
import asyncio
from db import connect_db
from telegram import Bot, Update
from telegram.ext import ContextTypes
import time  

# Telegram Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"
CHANNEL_USERNAME = "vessacommunity"  

bot = Bot(token=BOT_TOKEN)

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE, user_steps):
    """Checks if the user has joined the Telegram channel AFTER email confirmation."""
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
    chat_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id

    # ✅ Initialize failed attempts counter
    if user_id not in user_steps:
        user_steps[user_id] = {"failed_attempts": 0}

    # ✅ If user has already failed 5 times, force restart registration
    if user_steps[user_id]["failed_attempts"] >= 5:
        del user_steps[user_id]  # ❌ Reset registration
        await update.callback_query.message.reply_text("🚨 Too many failed attempts! Restart by typing /start.")
        return False  

    # ✅ Check membership using Telegram API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    
    try:
        response = requests.get(url).json()

        if response.get("ok"):
            status = response["result"]["status"]
            if status in ["member", "administrator", "creator"]:
                # ✅ User is a member → Proceed to save their details
                if "name" in user_steps[user_id]:  # Prevent saving empty user data
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

                            # ✅ Reset failed attempts and confirm success
                            user_steps[user_id]["failed_attempts"] = 0  
                            return True  

                        except Exception as e:
                            print(f"❌ Database error while saving user {user_id}: {e}")
                            conn.rollback()
                        finally:
                            conn.close()
                else:
                    print(f"❌ Missing user details for {user_id}. Skipping database save.")
                    return False
            else:
                # ❌ User is NOT a member → Increase failed attempts
                user_steps[user_id]["failed_attempts"] += 1

                # ⚠️ Show a warning after **2 failed attempts**
                if user_steps[user_id]["failed_attempts"] >= 2:
                    warning_message = await update.callback_query.message.reply_text(
                        "⚠️ You haven't joined the channel yet!\n"
                        "🚨 Please join first: [Join Here](https://t.me/vessacommunity)",
                        parse_mode="Markdown"
                    )

                    # 🕒 **Automatically delete the warning message after 2 seconds**
                    await asyncio.sleep(2)
                    try:
                        await context.bot.delete_message(chat_id=chat_id, message_id=warning_message.message_id)
                    except Exception:
                        pass  # ✅ Ignore errors if message is already deleted

                return False  

        else:
            print(f"❌ API error while checking membership for user {user_id}: {response}")
            return False  

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error checking Telegram membership: {e}")
        return False  

    except Exception as e:
        print(f"❌ Unexpected error in check_membership: {e}")
        return False  


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
                        except Exception as e:
                            print(f"❌ Error sending message to user {user_id}: {e}")  
                
                else:
                    print(f"Error checking membership for user {user_id}: {response}")  

                time.sleep(1)  # ✅ Prevent API rate limits

            cur.close()
        except Exception as e:
            print(f"Error verifying membership: {e}")
        finally:
            conn.close()  
