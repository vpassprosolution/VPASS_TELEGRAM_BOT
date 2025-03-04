from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import psycopg2
from db import connect_db

# List of Admin Telegram IDs (You can add multiple admins here)
ADMIN_IDS = [6756668018, 6596936867, 1829527460]  # Replace with actual admin Telegram IDs

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /admin command and shows admin options"""
    user_id = update.message.from_user.id

    # Check if the user is an admin
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized to access admin functions.")
        return

    # Create admin menu buttons
    keyboard = [
        [InlineKeyboardButton("➕ Add User", callback_data="admin_add_user")],
        [InlineKeyboardButton("❌ Delete User", callback_data="admin_delete_user")],
        [InlineKeyboardButton("🔍 Check User", callback_data="admin_check_user")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🔹 **Admin Panel** 🔹\nChoose an action:", reply_markup=reply_markup)

async def add_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts admin to enter user details"""
    query = update.callback_query
    await query.message.reply_text("📝 Please enter user details in this format:\n`user_id, name, username, contact, email`")
    context.user_data["admin_action"] = "add_user"

async def delete_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts admin to enter the user ID to delete"""
    query = update.callback_query
    await query.message.reply_text("🗑️ Enter the **user_id** of the user you want to delete:")
    context.user_data["admin_action"] = "delete_user"

async def check_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts admin to enter user ID to check"""
    query = update.callback_query
    await query.message.reply_text("🔍 Enter the **user_id** to check if the user exists:")
    context.user_data["admin_action"] = "check_user"

async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles admin input based on the selected action"""
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized to use admin commands.")
        return

    action = context.user_data.get("admin_action")
    if not action:
        await update.message.reply_text("⚠️ No admin action selected. Use /admin to access the panel.")
        return

    input_text = update.message.text.strip()
    
    conn = connect_db()
    if not conn:
        await update.message.reply_text("⚠️ Database connection error. Try again later.")
        return

    cur = conn.cursor()

    if action == "add_user":
        try:
            # Extract user details
            user_data = input_text.split(",")
            if len(user_data) != 5:
                await update.message.reply_text("⚠️ Incorrect format. Use: `user_id, name, username, contact, email`")
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
            await update.message.reply_text(f"✅ User `{user_id}` has been added/updated successfully.")

        except Exception as e:
            await update.message.reply_text(f"❌ Error adding user: {e}")

    elif action == "delete_user":
        try:
            cur.execute("DELETE FROM users WHERE user_id = %s", (input_text,))
            conn.commit()
            if cur.rowcount > 0:
                await update.message.reply_text(f"✅ User `{input_text}` has been deleted successfully.")
            else:
                await update.message.reply_text(f"⚠️ User `{input_text}` not found.")

        except Exception as e:
            await update.message.reply_text(f"❌ Error deleting user: {e}")

    elif action == "check_user":
        try:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (input_text,))
            user = cur.fetchone()
            if user:
                await update.message.reply_text(f"✅ User `{input_text}` exists in the database.")
            else:
                await update.message.reply_text(f"⚠️ User `{input_text}` does not exist.")

        except Exception as e:
            await update.message.reply_text(f"❌ Error checking user: {e}")

    cur.close()
    conn.close()
    context.user_data["admin_action"] = None  # Reset action

