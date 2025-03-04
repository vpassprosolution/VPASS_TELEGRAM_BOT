from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import psycopg2
from db import connect_db
from ai_sentiment import show_instruments, handle_instrument_selection

# Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"

# Step tracking for user registration
user_steps = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command"""
    user_id = update.message.from_user.id

    # Check if the user is already registered
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            username = user[0]
            keyboard = [[InlineKeyboardButton("Go to Main Menu", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Welcome back {username}", reply_markup=reply_markup)
            return

    # Send welcome image first
    welcome_image = "welcome.png"

    with open(welcome_image, "rb") as photo:
        await update.message.reply_photo(photo=photo)

    # Send welcome text with registration button
    keyboard = [[InlineKeyboardButton("COMPLETE YOUR REGISTRATION", callback_data="register")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_message = await update.message.reply_text("WELCOME TO VPASS PRO VERSION 2.0", reply_markup=reply_markup)

    # Store message ID so we can delete it later
    context.user_data["button_message"] = sent_message.message_id

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user registration when they click the button"""
    query = update.callback_query
    user_id = query.from_user.id

    # Delete the button after clicking
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data["button_message"])
    except Exception:
        pass  # Ignore errors if message doesn't exist

    # Start registration process
    user_steps[user_id] = {"step": "name"}
    sent_message = await query.message.reply_text("Please enter your name:")
    user_steps[user_id]["last_message_id"] = sent_message.message_id

async def collect_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collects user registration details step by step"""
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_input = update.message.text

    if user_id in user_steps:
        step = user_steps[user_id]["step"]

        # Delete the previous message
        try:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=user_steps[user_id]["last_message_id"])
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        except Exception:
            pass  # Ignore errors if message doesn't exist

        if step == "name":
            user_steps[user_id]["name"] = user_input
            user_steps[user_id]["step"] = "username"
            sent_message = await update.message.reply_text("Enter your Telegram username (without @):")
        
        elif step == "username":
            user_steps[user_id]["username"] = user_input
            user_steps[user_id]["step"] = "contact"
            sent_message = await update.message.reply_text("Enter your contact number:")
        
        elif step == "contact":
            user_steps[user_id]["contact"] = user_input
            user_steps[user_id]["step"] = "email"
            sent_message = await update.message.reply_text("Enter your email address:")
        
        elif step == "email":
            user_steps[user_id]["email"] = user_input

            # Save user data to the database (including Chat ID)
            conn = connect_db()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO users (user_id, chat_id, name, username, contact, email)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET chat_id = EXCLUDED.chat_id, 
                                      name = EXCLUDED.name, 
                                      username = EXCLUDED.username, 
                                      contact = EXCLUDED.contact, 
                                      email = EXCLUDED.email;
                        """,
                        (user_id, chat_id, user_steps[user_id]["name"], user_steps[user_id]["username"],
                         user_steps[user_id]["contact"], user_steps[user_id]["email"])
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                except Exception as e:
                    await update.message.reply_text(f"Error saving your data: {e}")

            # Remove user from tracking
            del user_steps[user_id]

            # Send confirmation message with a button
            keyboard = [[InlineKeyboardButton("START VPASS PRO NOW", callback_data="start_vpass_pro")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Registration complete, VPASS PRO V2 is now activated for full access.", reply_markup=reply_markup)
            return
        
        # Save the last sent message ID for deletion
        user_steps[user_id]["last_message_id"] = sent_message.message_id

    else:
        await update.message.reply_text("Please click **COMPLETE YOUR REGISTRATION** to begin registration.")

async def start_vpass_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'START VPASS PRO NOW' button click"""
    query = update.callback_query

    # Delete the previous message
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception:
        pass  # Ignore errors

    # Create the button menu
    keyboard = [
    [InlineKeyboardButton("VPASS SMART SIGNAL", callback_data="vpass_smart_signal")],
    [InlineKeyboardButton("VPASS AI SENTIMENT", callback_data="ai_sentiment")],
        [
            InlineKeyboardButton("Forex Factory", url="https://www.forexfactory.com"),
            InlineKeyboardButton("Discord", url="https://discord.com"),
            InlineKeyboardButton("ChatGPT", url="https://chat.openai.com"),
            InlineKeyboardButton("DeepSeek", url="https://www.deepseek.com")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Welcome, Select Your Preference", reply_markup=reply_markup)

def main():
    """Main function to run the bot"""
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(register_user, pattern="register"))
    app.add_handler(CallbackQueryHandler(start_vpass_pro, pattern="start_vpass_pro"))
    app.add_handler(CallbackQueryHandler(start_vpass_pro, pattern="main_menu"))
    app.add_handler(CallbackQueryHandler(show_instruments, pattern="ai_sentiment"))
    app.add_handler(CallbackQueryHandler(handle_instrument_selection, pattern="sentiment_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_user_data))

    print("Bot is running...")  # ✅ Ensure this is inside `main()` with the correct indentation

    app.run_polling()

if __name__ == "__main__":
    main()


