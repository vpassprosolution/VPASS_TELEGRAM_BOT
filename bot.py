from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import psycopg2
from db import connect_db
from admin import admin_panel, add_user_prompt, delete_user_prompt, check_user_prompt, handle_admin_input
import asyncio
import ai_signal_handler  # Import the AI Signal Handler
from telegram.ext import CallbackQueryHandler
import phone_verifier  # Import phone verification module


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

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user registration when they click the button"""
    query = update.callback_query
    user_id = query.from_user.id

    # Delete the button after clicking
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data["button_message"])
    except Exception:
        pass  

    # Start registration process
    user_steps[user_id] = {"step": "name"}
    sent_message = await query.message.reply_text("Please enter your name:")
    user_steps[user_id]["prompt_message_id"] = sent_message.message_id  

async def collect_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collects user registration details step by step"""
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_input = update.message.text

    # Debugging step: Print current user step
    print(f"Current step for user {user_id}: {user_steps.get(user_id, {}).get('step', 'Unknown')}")

    if user_id not in user_steps:
        user_steps[user_id] = {"step": "name"}  # ✅ Ensure user starts at the first step

    step = user_steps[user_id]["step"]
    sent_message = None  # ✅ Ensure `sent_message` is always initialized

    # ✅ Delete old messages (to keep chat clean)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        if "prompt_message_id" in user_steps[user_id]:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_steps[user_id]["prompt_message_id"])
    except Exception:
        pass  

    # ✅ Step 1: Ask for Name
    if step == "name":
        user_steps[user_id]["name"] = user_input
        user_steps[user_id]["step"] = "username"
        sent_message = await update.message.reply_text("📛 Enter your Telegram username (@username):")

    # ✅ Step 2: Ask for Username
    elif step == "username":
        user_steps[user_id]["username"] = user_input
        user_steps[user_id]["step"] = "contact"
        sent_message = await update.message.reply_text("📞 Enter your phone number (e.g., +1234567890):")

    # ✅ Step 3: Handle Phone Number (Ensures OTP is sent before proceeding)
    elif step == "contact":
        if not phone_verifier.validate_phone_number(user_input):
            sent_message = await update.message.reply_text(
                "❌ Invalid phone number format.\n📌 Please enter a valid phone number in international format (e.g., +1234567890):"
            )
        else:
            user_steps[user_id]["contact"] = user_input
            otp_sent = await phone_verifier.send_telegram_otp(context, user_input)

            if otp_sent:
                user_steps[user_id]["step"] = "verify_phone"
                sent_message = await update.message.reply_text(
                    "📩 OTP has been sent to your Telegram inbox.\n"
                    "📌 Please check your Telegram messages and enter the code here to verify:"
                )
            else:
                sent_message = await update.message.reply_text(
                    "❌ Failed to send OTP. Please make sure you entered a valid Telegram phone number."
                )

    # ✅ Step 4: Ensure OTP verification before proceeding
    elif step == "verify_phone":
        phone_number = user_steps[user_id]["contact"]
        is_verified = await phone_verifier.verify_otp(phone_number, user_input)

        if is_verified:
            user_steps[user_id]["step"] = "email"
            sent_message = await update.message.reply_text("✅ Phone verified!\n📧 Please enter your email address:")
        else:
            user_steps[user_id]["step"] = "verify_phone"  # Ensure user stays in OTP step
            sent_message = await update.message.reply_text("❌ Incorrect OTP. Please try again:")

    # ✅ Step 5: Ask for Email and Save Data to Database
    elif step == "email":
        if "@" not in user_input or "." not in user_input:
            sent_message = await update.message.reply_text("❌ Invalid email format. Please enter a valid email address:")
        else:
            user_steps[user_id]["email"] = user_input  # Save email
            user_steps[user_id]["step"] = "complete"  # ✅ Move to final step

            # ✅ Save user data to the database
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
                    sent_message = await update.message.reply_text(f"❌ Error saving your data: {e}")

            # ✅ Confirm registration complete
            keyboard = [[InlineKeyboardButton("START VPASS PRO NOW", callback_data="start_vpass_pro")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await update.message.reply_text("✅ Registration complete! VPASS PRO is now activated.", reply_markup=reply_markup)

    else:
        # ❌ Handle unknown steps (Debugging)
        sent_message = await update.message.reply_text("⚠️ Unexpected error. Please restart your registration.")
        print(f"❌ Error: User {user_id} is in an unknown state: {step}")

    # ✅ Store last sent prompt message ID for deletion
    if sent_message:
        user_steps[user_id]["prompt_message_id"] = sent_message.message_id

            # ✅ Confirm registration complete
            keyboard = [[InlineKeyboardButton("START VPASS PRO NOW", callback_data="start_vpass_pro")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await update.message.reply_text("✅ Registration complete! VPASS PRO is now activated.", reply_markup=reply_markup)

        else:
            # ❌ Handle unknown steps (Debugging)
            sent_message = await update.message.reply_text("⚠️ Unexpected error. Please restart your registration.")
            print(f"❌ Error: User {user_id} is in an unknown state: {step}")

        # ✅ Store last sent prompt message ID for deletion
        if sent_message:
            user_steps[user_id]["prompt_message_id"] = sent_message.message_id


            # ✅ Confirm registration complete
            keyboard = [[InlineKeyboardButton("START VPASS PRO NOW", callback_data="start_vpass_pro")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await update.message.reply_text("✅ Registration complete! VPASS PRO is now activated.", reply_markup=reply_markup)

        else:
            # ❌ Handle unknown steps (Debugging)
            sent_message = await update.message.reply_text("⚠️ Unexpected error. Please restart your registration.")
            print(f"❌ Error: User {user_id} is in an unknown state: {step}")

        # ✅ Store last sent prompt message ID for deletion
        if sent_message:  # ✅ Only store message ID if `sent_message` exists
            user_steps[user_id]["prompt_message_id"] = sent_message.message_id




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


