from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import psycopg2
from db import connect_db
from admin import admin_panel, add_user_prompt, delete_user_prompt, check_user_prompt, handle_admin_input
import asyncio
import ai_signal_handler  # Import the AI Signal Handler
from telegram.ext import CallbackQueryHandler
import re
from telegram.ext import ContextTypes
from channel_verification import check_membership
from telegram.ext import JobQueue
from ai_technical import (
    show_technical_menu,
    show_instrument_menu,
    show_timeframe_menu,
    handle_technical_selection,
    back_to_technical_menu,
    back_to_technical_instruments  # ✅ Ensure this exists
)




# Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"

# Step tracking for user registration
user_steps = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and starts user registration."""
    from ai_sentiment import show_instruments  

    user_id = update.message.from_user.id

    # ✅ Check if the user is already registered
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

    # ✅ Do NOT check membership here! We allow users to register first.

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
    """Collects user registration details step by step and forwards them to channel verification"""
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_input = update.message.text

    if user_id in user_steps:
        step = user_steps[user_id]["step"]

        # ✅ Delete user's input message and previous bot message
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)  # Delete user's message
            await context.bot.delete_message(chat_id=chat_id, message_id=user_steps[user_id]["prompt_message_id"])  # Delete bot's prompt
        except Exception:
            pass  # Ignore errors if already deleted

        if step == "name":
            user_steps[user_id]["name"] = user_input
            user_steps[user_id]["step"] = "username"
            sent_message = await update.message.reply_text("📛 Enter your Telegram username (@username):")

        elif step == "username":
            user_steps[user_id]["username"] = user_input
            user_steps[user_id]["step"] = "contact"
            sent_message = await update.message.reply_text("📞 Enter your phone number (e.g., +601123020037):")

        elif step == "contact":
            if not re.match(r"^\+\d{7,15}$", user_input):
                sent_message = await update.message.reply_text("❌ Invalid phone number. Please enter in international format (e.g., +601123020037):")
            else:
                user_steps[user_id]["contact"] = user_input
                user_steps[user_id]["step"] = "confirm_contact"

                # ✅ Ask for confirmation with buttons
                keyboard = [
                    [InlineKeyboardButton("✅ Confirm", callback_data="confirm_phone")],
                    [InlineKeyboardButton("🔄 Retake", callback_data="reenter_phone")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                sent_message = await update.message.reply_text(f"📞 You entered: {user_input}\n\nIs this correct?", reply_markup=reply_markup)

        elif step == "email":
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user_input):
                sent_message = await update.message.reply_text("❌ Invalid email format. Please enter a valid email address:")
            else:
                user_steps[user_id]["email"] = user_input
                user_steps[user_id]["step"] = "confirm_email"

                # ✅ Ask for confirmation with buttons
                keyboard = [
                    [InlineKeyboardButton("✅ Confirm", callback_data="confirm_email")],
                    [InlineKeyboardButton("🔄 Retake", callback_data="reenter_email")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                sent_message = await update.message.reply_text(f"📧 You entered: {user_input}\n\nIs this correct?", reply_markup=reply_markup)

        # ✅ Store last bot message ID for deletion
        user_steps[user_id]["prompt_message_id"] = sent_message.message_id

async def confirm_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles confirmation of the phone number"""
    query = update.callback_query
    user_id = query.from_user.id

    # ✅ Acknowledge button press
    await query.answer()

    if query.data == "confirm_phone":
        user_steps[user_id]["step"] = "email"
        await query.message.edit_text("📧 Enter your email address:")

    elif query.data == "reenter_phone":
        # ✅ Ask user to enter phone number again
        user_steps[user_id]["step"] = "contact"
        await query.message.edit_text("📞 Please enter your phone number again (e.g., +601123020037):")

async def confirm_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles email confirmation & asks user to verify Telegram channel membership"""
    query = update.callback_query
    user_id = query.from_user.id

    # ✅ Acknowledge button press
    await query.answer()

    if query.data == "confirm_email":
        # ✅ Now the user must join the Telegram channel
        user_steps[user_id]["step"] = "check_membership"

        keyboard = [[InlineKeyboardButton("✅ I Have Joined", callback_data="check_membership")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            "✅ Email confirmed!\n\n"
            "🚨 Before you can continue, you **must** join our Telegram channel:\n"
            "🔗 [Join Here](https://t.me/vessacommunity)\n\n"
            "Once you've joined, click the button below:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    elif query.data == "reenter_email":
        # ✅ Ask user to enter email again
        user_steps[user_id]["step"] = "email"
        await query.message.edit_text("📧 Please enter your email address again:")


async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the '✅ I Have Joined' button by checking if the user joined the Telegram channel."""
    from channel_verification import check_membership  # ✅ Import function inside to prevent circular import
    global user_steps

    query = update.callback_query
    await query.answer()  # ✅ Acknowledge button press (prevents UI bugs)

    user_id = query.from_user.id

    if user_id in user_steps:
        # Track failed attempts
        if "failed_attempts" not in user_steps[user_id]:
            user_steps[user_id]["failed_attempts"] = 0

        # ✅ Call the function to check membership
        is_member = await check_membership(update, context, user_steps)

        if is_member:  # ✅ If user has joined the channel
            del user_steps[user_id]  # ✅ Remove user from pending registration list
            keyboard = [[InlineKeyboardButton("Go to Main Menu", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            new_text = "✅ Membership verified! Welcome to VPASS PRO.\nClick below to continue:"

            # ✅ Check if the message text is already the same before updating
            try:
                if query.message.text != new_text:
                    await query.message.edit_text(new_text, reply_markup=reply_markup)
            except Exception as e:
                if "Message is not modified" in str(e):
                    pass  # ✅ Ignore this specific error
                else:
                    print(f"❌ Unexpected error updating message: {e}")  # Log other unexpected errors

        else:
            # ❌ User is still NOT a member → Increase failed attempts
            user_steps[user_id]["failed_attempts"] += 1

            keyboard = [[InlineKeyboardButton("✅ I Have Joined", callback_data="check_membership")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            new_text = (
                "❌ You have NOT joined the channel!\n\n"
                "🚨 Please **join here first:** [Join Here](https://t.me/vessacommunity)\n"
                "Then click '✅ I Have Joined' again."
            )

            # ✅ Check if the message text is already the same before updating
            try:
                if query.message.text != new_text:
                    await query.message.edit_text(new_text, parse_mode="Markdown", reply_markup=reply_markup)
            except Exception as e:
                if "Message is not modified" in str(e):
                    pass  # ✅ Ignore this specific error
                else:
                    print(f"❌ Unexpected error updating message: {e}")  # Log other unexpected errors

            # ⚠️ After 2 failed attempts, show a **temporary warning message**
            if user_steps[user_id]["failed_attempts"] >= 2:
                warning_message = await query.message.reply_text(
                    "⚠️ You haven't joined the channel yet!\n"
                    "🚨 Please join first: [Join Here](https://t.me/vessacommunity)",
                    parse_mode="Markdown"
                )

                # 🕒 **Automatically delete the warning message after 2 seconds**
                await asyncio.sleep(2)
                try:
                    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=warning_message.message_id)
                except Exception:
                    pass  # ✅ Ignore errors if message is already deleted

            # ❌ After **5 failed attempts**, force the user to restart
            if user_steps[user_id]["failed_attempts"] >= 5:
                del user_steps[user_id]  # ✅ Reset user data
                await query.message.reply_text(
                    "🚨 Too many failed attempts! Restart the process by typing /start."
                )
    else:
        await query.message.reply_text("❌ Registration process not found. Please restart by typing /start.")


async def start_vpass_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'START VPASS PRO NOW' button click"""
    query = update.callback_query

    # Redirect to main menu
    await main_menu(update, context)

def main():
    """Main function to run the bot"""
    from ai_sentiment import show_instruments, handle_instrument_selection  
    from channel_verification import verify_active_membership  # ✅ Import the periodic check

    app = Application.builder().token(BOT_TOKEN).build()
    job_queue = app.job_queue

    # ✅ Run membership verification every 30 minutes
    job_queue.run_repeating(verify_active_membership, interval=1800, first=10)  
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
    app.add_handler(CallbackQueryHandler(confirm_email, pattern="confirm_email"))
    app.add_handler(CallbackQueryHandler(confirm_email, pattern="reenter_email"))
    app.add_handler(CallbackQueryHandler(check_membership_callback, pattern="check_membership"))  # ✅ Membership Verification

    

    # Connect "VPASS SMART SIGNAL" button to subscription system
    from subscription_handler import show_instruments, show_subscription_menu, subscribe, unsubscribe, back_to_main, back_to_instruments

    app.add_handler(CallbackQueryHandler(show_instruments, pattern="vpass_smart_signal"))
    app.add_handler(CallbackQueryHandler(show_subscription_menu, pattern="^select_"))
    app.add_handler(CallbackQueryHandler(subscribe, pattern="^subscribe_"))
    app.add_handler(CallbackQueryHandler(unsubscribe, pattern="^unsubscribe_"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="back_to_main"))
    app.add_handler(CallbackQueryHandler(back_to_instruments, pattern="back_to_instruments"))
    app.add_handler(CallbackQueryHandler(show_technical_menu, pattern="^ai_technical$"))
    app.add_handler(CallbackQueryHandler(show_instrument_menu, pattern="^category_.*$"))
    app.add_handler(CallbackQueryHandler(show_timeframe_menu, pattern="^instrument_.*$"))
    app.add_handler(CallbackQueryHandler(handle_technical_selection, pattern="^timeframe_.*$"))
    # ✅ Registering Correct Callback Handlers for Back Buttons
    app.add_handler(CallbackQueryHandler(back_to_technical_menu, pattern="^back_to_technical_menu$"))
    app.add_handler(CallbackQueryHandler(back_to_technical_instruments, pattern="^back_to_technical_instruments$"))

   



    print("Bot is running...")

    app.run_polling()

if __name__ == "__main__":
    main()
