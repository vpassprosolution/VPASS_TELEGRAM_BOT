import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import connect_db
from channel_verification import check_membership
from user_state import user_steps


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
    if not update.message:
        return  # ✅ Skip this function if it's not a user text message

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
            sent_message = await update.message.reply_text("Enter your Telegram username (@username):")

        elif step == "username":
            user_steps[user_id]["username"] = user_input
            user_steps[user_id]["step"] = "contact"
            sent_message = await update.message.reply_text("📞 Enter your phone number (e.g., +601234567890):")

        elif step == "contact":
            if not re.match(r"^\+\d{7,15}$", user_input):
                sent_message = await update.message.reply_text("❌ Invalid phone number. Please enter in international format (e.g., +601123020037):")
            else:
                user_steps[user_id]["contact"] = user_input
                user_steps[user_id]["step"] = "confirm_contact"

                # ✅ Side-by-side buttons for phone
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Retake", callback_data="reenter_phone"),
                        InlineKeyboardButton("✅ Confirm", callback_data="confirm_phone")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                sent_message = await update.message.reply_text(
                    f"📞 You entered: {user_input}\n\nIs this correct?", reply_markup=reply_markup)

        elif step == "email":
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user_input):
                sent_message = await update.message.reply_text("❌ Invalid email format. Please enter a valid email address:")
            else:
                user_steps[user_id]["email"] = user_input
                user_steps[user_id]["step"] = "confirm_email"

                # ✅ Side-by-side buttons for email
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Retake", callback_data="reenter_email"),
                        InlineKeyboardButton("✅ Confirm", callback_data="confirm_email")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                sent_message = await update.message.reply_text(
                    f"📧 You entered: {user_input}\n\nIs this correct?", reply_markup=reply_markup)

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
        await query.message.edit_text("📞 Please enter your phone number again (e.g., +601234567890):")

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
            keyboard = [[InlineKeyboardButton("START VESSA PRO NOW", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            new_text = "✅ ✅ ✅Membership verified!✅ ✅ ✅"

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