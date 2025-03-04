from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import psycopg2
from db import connect_db

# List of Admin Telegram IDs
ADMIN_IDS = [6756668018, 6596936867, 1829527460]  

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /admin command and shows admin options"""
    user_id = update.message.from_user.id

    # Delete the /admin command message
    try:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    except Exception:
        pass  

    # Check if the user is an admin
    if user_id not in ADMIN_IDS:
        return  

    # Create admin menu buttons
    keyboard = [
        [InlineKeyboardButton("➕ Add User", callback_data="admin_add_user")],
        [InlineKeyboardButton("❌ Delete User", callback_data="admin_delete_user")],
        [InlineKeyboardButton("🔍 Check User", callback_data="admin_check_user")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    sent_message = await update.message.reply_text("🔹 **Admin Panel** 🔹\nChoose an action:", reply_markup=reply_markup)
    
    # Store message ID to delete later
    context.user_data["admin_panel_message"] = sent_message.message_id

async def delete_admin_message(context, chat_id, message_id):
    """Helper function to delete messages after a delay"""
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass  

async def add_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts admin to enter user details"""
    query = update.callback_query
    chat_id = query.message.chat_id

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    except Exception:
        pass  

    sent_message = await query.message.reply_text("📝 Enter user details:\n`user_id, name, username, contact, email`")
    context.user_data["admin_action"] = "add_user"
    context.user_data["last_admin_message"] = sent_message.message_id  

async def delete_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts admin to enter user ID to delete"""
    query = update.callback_query
    chat_id = query.message.chat_id

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    except Exception:
        pass  

    sent_message = await query.message.reply_text("🗑️ Enter **user_id** to delete:")
    context.user_data["admin_action"] = "delete_user"
    context.user_data["last_admin_message"] = sent_message.message_id  

async def check_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts admin to enter user ID to check"""
    query = update.callback_query
    chat_id = query.message.chat_id

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    except Exception:
        pass  

    sent_message = await query.message.reply_text("🔍 Enter **user_id** to check:")
    context.user_data["admin_action"] = "check_user"
    context.user_data["last_admin_message"] = sent_message.message_id  

async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles admin input based on selected action"""
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if user_id not in ADMIN_IDS:
        return  

    action = context.user_data.get("admin_action")
    if not action:
        return  

    input_text = update.message.text.strip()
    
    conn = connect_db()
    if not conn:
        return  

    cur = conn.cursor()

    if action == "add_user":
        try:
            user_data = input_text.split(",")
            if len(user_data) != 5:
                sent_message = await update.message.reply_text("⚠️ Incorrect format. Use: `user_id, name, username, contact, email`")
                context.user_data["last_admin_message"] = sent_message.message_id  
                return

            user_id, name, username, contact, email = map(str.strip, user_data)

            cur.execute(
                """
                INSERT INTO users (user_id, name, username, contact, email)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET name = EXCLUDED.name, 
                              username = EXCLUDED.username, 
                              contact = EXCLUDED.contact, 
                              email = EXCLUDED.email;
                """,
                (user_id, name, username, contact, email)
            )
            conn.commit()
            sent_message = await update.message.reply_text(f"✅ User `{user_id}` added/updated successfully.")

        except Exception as e:
            sent_message = await update.message.reply_text(f"❌ Error adding user: {e}")

    elif action == "delete_user":
        try:
            cur.execute("DELETE FROM users WHERE user_id = %s", (input_text,))
            conn.commit()
            if cur.rowcount > 0:
                sent_message = await update.message.reply_text(f"✅ User `{input_text}` deleted successfully.")
            else:
                sent_message = await update.message.reply_text(f"⚠️ User `{input_text}` not found.")

        except Exception as e:
            sent_message = await update.message.reply_text(f"❌ Error deleting user: {e}")

    elif action == "check_user":
        try:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (input_text,))
            user = cur.fetchone()
            if user:
                sent_message = await update.message.reply_text(f"✅ User `{input_text}` exists in the database.")
            else:
                sent_message = await update.message.reply_text(f"⚠️ User `{input_text}` does not exist.")

        except Exception as e:
            sent_message = await update.message.reply_text(f"❌ Error checking user: {e}")

    cur.close()
    conn.close()

    # Delete the messages after 5 seconds
    await delete_admin_message(context, chat_id, sent_message.message_id)

    if "last_admin_message" in context.user_data:
        await delete_admin_message(context, chat_id, context.user_data["last_admin_message"])

    context.user_data["admin_action"] = None  

