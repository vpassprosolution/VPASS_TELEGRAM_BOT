from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import psycopg2
from db import connect_db
from admin import admin_panel, add_user_prompt, delete_user_prompt, check_user_prompt, handle_admin_input
import asyncio
import ai_signal_handler  # Import the AI Signal Handler
from telegram.ext import CallbackQueryHandler
import re
from channel_verification import is_user_in_channel
from db import update_channel_status, get_user_status

# Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"

# Step tracking for user registration
user_steps = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command"""
    from ai_sentiment import show_instruments  

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
            await update.message.reply_text(f"🌑 Welcome back to world of AI {username}🌑", reply_markup=reply_markup)
            return

    # Send welcome image
    welcome_image = "welcome.png"

    with open(welcome_image, "rb") as photo:
        await update.message.reply_photo(photo=photo)

    # Send welcome text with registration button
    keyboard = [[InlineKeyboardButton("COMPLETE YOUR REGISTRATION", callback_data="register")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_message = await update.message.reply_text("WELCOME TO VPASS PRO VERSION 2.0", reply_markup=reply_markup)

    # Store message ID so we can delete it later
    context.user_data["button_message"] = sent_message.message_id



async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns to the main menu"""
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("VPASS SMART SIGNAL", callback_data="vpass_smart_signal")],
        [InlineKeyboardButton("VPASS AI SENTIMENT", callback_data="ai_sentiment")],
        [InlineKeyboardButton("VPASS AI TECHNICAL ANALYSIS", callback_data="ai_technical")],  # New button
        [InlineKeyboardButton("AI AGENT INSTANT SIGNAL", callback_data="ai_agent_signal")],
        [InlineKeyboardButton("🔥 NEWS WAR ROOM 🔥", callback_data="news_war_room")],  # Updated button
        [
            InlineKeyboardButton("F.Factory", url="https://www.forexfactory.com"),
            InlineKeyboardButton("Discord", url="https://discordapp.com/channels/1347220972519952497/1347220976689086577"),
            InlineKeyboardButton("ChatGPT", url="https://chat.openai.com"),
            InlineKeyboardButton("DeepSeek", url="https://www.deepseek.com")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        "*WELCOME TO VPASS PRO VERSION V2*\n"
        "   The Future of Intelligent Starts Here\n"
        "          *CHOOSE YOUR STRATEGY*",
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )

# Function to trigger AI signal menu from ai_signal_handler.py
async def ai_agent_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ai_signal_handler.show_instruments(update, context)



async def show_vip_room_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows VIP message with 'I UNDERSTAND' button"""
    query = update.callback_query

    # Create "I UNDERSTAND" button
    keyboard = [[InlineKeyboardButton("I UNDERSTAND", callback_data="delete_vip_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send VIP message (so it can be deleted)
    await query.message.reply_text(
        "✨ *EXCLUSIVE VPASS PRO ACCESS* ✨\n"
        "✨ *VIP MEMBERS ONLY* ✨\n\n"
        "This space is reserved for our esteemed VIP subscribers.\n\n"
        "For inquiries or to elevate your experience, kindly contact the administration.\n\n"
        "We appreciate your understanding and look forward to welcoming you.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def delete_vip_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes the VIP message when 'I UNDERSTAND' button is clicked"""
    query = update.callback_query
    await query.answer()  # Acknowledge button press

    # Delete the button and message itself
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception:
        pass  # Ignore errors if already deleted

user_steps = {}

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the registration process by asking for the user's name."""
    user_id = update.message.from_user.id
    user_steps[user_id] = {"step": "name"}

    await update.message.reply_text("📛 Please enter your full name:")

async def collect_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collects user registration details step by step."""
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_input = update.message.text

    if user_id in user_steps:
        step = user_steps[user_id]["step"]

        if step == "name":
            user_steps[user_id]["name"] = user_input
            user_steps[user_id]["step"] = "username"
            await update.message.reply_text("📛 Enter your Telegram username (@username):")

        elif step == "username":
            user_steps[user_id]["username"] = user_input
            user_steps[user_id]["step"] = "contact"
            await update.message.reply_text("📞 Enter your phone number (e.g., +601123020037):")

        elif step == "contact":
            if not re.match(r"^\+\d{7,15}$", user_input):
                await update.message.reply_text("❌ Invalid phone number. Please enter in international format (e.g., +601123020037):")
            else:
                user_steps[user_id]["contact"] = user_input
                user_steps[user_id]["step"] = "email"
                await update.message.reply_text("📧 Enter your email address:")

        elif step == "email":
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user_input):
                await update.message.reply_text("❌ Invalid email format. Please enter a valid email address:")
            else:
                user_steps[user_id]["email"] = user_input

                # ✅ Save user data to the database
                conn = connect_db()
                if conn:
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            """
                            INSERT INTO users (user_id, chat_id, name, username, contact, email, joined_channel)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (user_id) 
                            DO UPDATE SET chat_id = EXCLUDED.chat_id, 
                                          name = EXCLUDED.name, 
                                          username = EXCLUDED.username, 
                                          contact = EXCLUDED.contact, 
                                          email = EXCLUDED.email,
                                          joined_channel = EXCLUDED.joined_channel;
                            """,
                            (user_id, chat_id, user_steps[user_id]["name"], user_steps[user_id]["username"],
                            user_steps[user_id]["contact"], user_steps[user_id]["email"], False)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        await update.message.reply_text(f"❌ Error saving your data: {e}")
                
                # ✅ Force the user to join the Telegram community
                keyboard = [[InlineKeyboardButton("✅ I Have Joined", callback_data="check_membership")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    "🚫 You must join [Vessa Community](https://t.me/vessacommunity) before accessing the bot.\n\n"
                    "🔹 **After joining, click the button below.**",
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )

                return  # ⛔ Stops registration here!

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks if the user has joined the channel after clicking 'I Have Joined'."""
    query = update.callback_query
    user_id = query.from_user.id

    if is_user_in_channel(user_id):
        update_channel_status(user_id, True)  # ✅ Mark user as joined

        # ✅ Show "Registration Complete" after user verifies membership
        keyboard = [[InlineKeyboardButton("START VPASS PRO NOW", callback_data="start_vpass_pro")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            "✅ You have successfully joined the channel!\n\n"
            "Click below to start VPASS PRO.",
            reply_markup=reply_markup
        )

    else:
        await query.message.edit_text(
            "🚫 You are still not in the channel!\n\n"
            "🔹 **Please join [Vessa Community](https://t.me/vessacommunity) and click the button again.**",
            parse_mode="Markdown"
        )

async def start_vpass_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'START VPASS PRO NOW' button click"""
    query = update.callback_query
    user_id = query.from_user.id

    email_verified, joined_channel = get_user_status(user_id)

    if not joined_channel:
        await query.message.edit_text(
            "🚫 You are still not in the channel!\n\n"
            "🔹 **Please join [Vessa Community](https://t.me/vessacommunity) and click '✅ I Have Joined' before starting.**",
            parse_mode="Markdown"
        )
        return

    await query.message.edit_text("✅ Registration complete! VPASS PRO is now activated.")

    # Redirect to the main menu (You can add your main menu function here)

async def confirm_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles confirmation of the phone number"""
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "confirm_phone":
        # ✅ Move to email step
        user_steps[user_id]["step"] = "email"
        await query.message.edit_text("📧 Enter your email address:")

    elif query.data == "reenter_phone":
        # ✅ Ask user to enter phone number again
        user_steps[user_id]["step"] = "contact"
        await query.message.edit_text("📞 Please enter your phone number again (e.g., +601123020037):")


async def start_vpass_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'START VPASS PRO NOW' button click"""
    query = update.callback_query

    # Redirect to main menu
    await main_menu(update, context)

def main():
    """Main function to run the bot"""
    from ai_sentiment import show_instruments, handle_instrument_selection  

    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(register_user, pattern="register"))
    app.add_handler(CallbackQueryHandler(start_vpass_pro, pattern="start_vpass_pro"))  # ✅ FIXED
    app.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))
    app.add_handler(CallbackQueryHandler(show_instruments, pattern="ai_sentiment"))  
    app.add_handler(CallbackQueryHandler(handle_instrument_selection, pattern="sentiment_"))  
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(add_user_prompt, pattern="admin_add_user"))
    app.add_handler(CallbackQueryHandler(delete_user_prompt, pattern="admin_delete_user"))
    app.add_handler(CallbackQueryHandler(check_user_prompt, pattern="admin_check_user"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_user_data))  
    app.add_handler(CallbackQueryHandler(ai_agent_signal, pattern="ai_agent_signal"))  # ✅ New AI button handler
    app.add_handler(CallbackQueryHandler(ai_signal_handler.fetch_ai_signal, pattern="^ai_signal_"))
    app.add_handler(CallbackQueryHandler(show_vip_room_message, pattern="news_war_room"))
    app.add_handler(CallbackQueryHandler(delete_vip_message, pattern="delete_vip_message"))
    app.add_handler(CallbackQueryHandler(confirm_phone_number, pattern="confirm_phone"))
    app.add_handler(CallbackQueryHandler(confirm_phone_number, pattern="reenter_phone"))
    app.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))

    

    # Connect "VPASS SMART SIGNAL" button to subscription system
    from subscription_handler import show_instruments, show_subscription_menu, subscribe, unsubscribe, back_to_main, back_to_instruments
    from ai_technical import show_technical_menu, show_timeframe_menu, handle_technical_selection

    app.add_handler(CallbackQueryHandler(show_instruments, pattern="vpass_smart_signal"))
    app.add_handler(CallbackQueryHandler(show_subscription_menu, pattern="^select_"))
    app.add_handler(CallbackQueryHandler(subscribe, pattern="^subscribe_"))
    app.add_handler(CallbackQueryHandler(unsubscribe, pattern="^unsubscribe_"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="back_to_main"))
    app.add_handler(CallbackQueryHandler(back_to_instruments, pattern="back_to_instruments"))
    app.add_handler(CallbackQueryHandler(show_technical_menu, pattern="^ai_technical$"))
    app.add_handler(CallbackQueryHandler(show_timeframe_menu, pattern="^instrument_.*$"))
    app.add_handler(CallbackQueryHandler(handle_technical_selection, pattern="^timeframe_.*$"))
    app.add_handler(CallbackQueryHandler(show_technical_menu, pattern="^back_to_technical_instruments$"))
    
   



    print("Bot is running...")

    app.run_polling()

import os

if __name__ == "__main__":
    lock_file = "/tmp/bot_running.lock"

    if os.path.exists(lock_file):
        print("❌ Another instance of the bot is already running. Exiting...")
    else:
        with open(lock_file, "w") as f:
            f.write("running")

        print("✅ Starting the bot...")
        main()

