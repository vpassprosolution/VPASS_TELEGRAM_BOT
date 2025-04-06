import httpx
import asyncio
from db import connect_db
from telegram import Bot, Update
from telegram.ext import ContextTypes
import time
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "vessacommunity"
bot = Bot(token=BOT_TOKEN)



async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE, user_steps):
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
    chat_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id

    if user_id not in user_steps:
        user_steps[user_id] = {"failed_attempts": 0}

    if user_steps[user_id]["failed_attempts"] >= 5:
        del user_steps[user_id]
        await update.callback_query.message.reply_text("🚨 Too many failed attempts! Restart by typing /start.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            response = resp.json()

        if response.get("ok"):
            status = response["result"]["status"]
            if status in ["member", "administrator", "creator"]:
                if "name" in user_steps[user_id]:
                    conn = connect_db()
                    if conn:
                        try:
                            cur = conn.cursor()
                            cur.execute(
                                """
                                INSERT INTO users (user_id, chat_id, name, username, contact, email, is_member)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (user_id) DO UPDATE SET
                                    chat_id = EXCLUDED.chat_id,
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
                            user_steps[user_id]["failed_attempts"] = 0
                            return True
                        except Exception as e:
                            print(f"❌ DB Error: {e}")
                            conn.rollback()
                        finally:
                            conn.close()
                else:
                    print(f"❌ Missing user details for {user_id}")
                    return False
            else:
                user_steps[user_id]["failed_attempts"] += 1
                if user_steps[user_id]["failed_attempts"] >= 2:
                    warn = await update.callback_query.message.reply_text(
                        "⚠️ You haven't joined the channel yet!\n"
                        "🚨 Please join first: [Join Here](https://t.me/vessacommunity)",
                        parse_mode="Markdown"
                    )
                    await asyncio.sleep(2)
                    try:
                        await context.bot.delete_message(chat_id=chat_id, message_id=warn.message_id)
                    except:
                        pass
                return False
        else:
            print(f"❌ API Error: {response}")
            return False

    except Exception as e:
        print(f"❌ Network/Other Error: {e}")
        return False


async def verify_active_membership(context: ContextTypes.DEFAULT_TYPE):
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE is_member = TRUE;")
            users = cur.fetchall()

            async with httpx.AsyncClient(timeout=10) as client:
                for user in users:
                    user_id = user[0]
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
                    try:
                        resp = await client.get(url)
                        response = resp.json()

                        if response.get("ok"):
                            status = response["result"]["status"]
                            if status not in ["member", "administrator", "creator"]:
                                cur.execute("UPDATE users SET is_member = FALSE WHERE user_id = %s;", (user_id,))
                                conn.commit()
                                try:
                                    await bot.send_message(
                                        chat_id=user_id,
                                        text="🚨 You left the VIP channel and lost access to VPASS PRO. Please rejoin to continue."
                                    )
                                except Exception as e:
                                    print(f"❌ Message send fail: {e}")
                        else:
                            print(f"⚠️ API error for {user_id}: {response}")

                        await asyncio.sleep(1)  # delay between requests

                    except Exception as e:
                        print(f"❌ Error checking user {user_id}: {e}")

            cur.close()
        except Exception as e:
            print(f"❌ Membership verification error: {e}")
        finally:
            conn.close()
