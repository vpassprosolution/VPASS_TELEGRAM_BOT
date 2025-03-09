import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# API URL (Update this to your Railway-deployed API)
API_URL = "https://vpasscopysignal-production.up.railway.app"

# ✅ Function: Handle VPASS COPY SIGNAL Button
async def handle_vpass_copy_signal_button(update: Update, context: CallbackContext) -> None:
    """Handles the VPASS COPY SIGNAL button and shows options."""
    query = update.callback_query
    await query.message.delete()
    keyboard = [
        [InlineKeyboardButton("📢 Another Telegram Group", callback_data="copy_telegram")],
        [InlineKeyboardButton("📈 TradingView (Coming Soon)", callback_data="ignore")],
        [InlineKeyboardButton("⬅ Back", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("📡 *Choose Your Copy Signal Source:*", parse_mode="Markdown", reply_markup=reply_markup)

# ✅ Function: Handle "Another Telegram Group" Button
async def handle_copy_telegram_button(update: Update, context: CallbackContext) -> None:
    """Handles the 'Another Telegram Group' button."""
    query = update.callback_query
    await query.message.delete()
    keyboard = [
        [InlineKeyboardButton("➕ Add New Telegram Group", callback_data="add_new_group")],
        [InlineKeyboardButton("📋 Check List Copy Signal", callback_data="check_list")],
        [InlineKeyboardButton("⬅ Back", callback_data="vpass_copy_signal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("📡 Choose an action:", reply_markup=reply_markup)

# ✅ Function: Handle User Text Input for Group Link & Signal Format
async def handle_text_messages(update: Update, context: CallbackContext) -> None:
    """Handles user text input for collecting group link and signal format."""
    if context.user_data.get("waiting_for_group_link"):
        return await collect_group_link(update, context)
    elif context.user_data.get("waiting_for_signal_format"):
        return await collect_signal_format(update, context)

# ✅ Function: Ask for Group Link
async def ask_group_link(update: Update, context: CallbackContext) -> None:
    """Asks the user to provide a Telegram group link."""
    query = update.callback_query
    await query.message.delete()
    keyboard = [[InlineKeyboardButton("⬅ Back", callback_data="copy_telegram")]]  # ✅ FIXED: Correct back button
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("🔗 Please send the Telegram group link where you want to copy signals from:", reply_markup=reply_markup)
    context.user_data["waiting_for_group_link"] = True  # ✅ Ensuring the flag is set correctly

# ✅ Function: Collect Group Link
async def collect_group_link(update: Update, context: CallbackContext) -> None:
    """Receives the Telegram group link and asks for signal format."""
    if context.user_data.get("waiting_for_group_link"):
        await update.message.delete()
        group_link = update.message.text.strip()

        if not group_link.startswith("https://t.me/"):
            await update.message.reply_text("⚠️ Invalid input! Please send a valid Telegram group link.")
            return

        context.user_data["group_link"] = group_link
        del context.user_data["waiting_for_group_link"]
        await update.message.reply_text("✅ Group link saved! Now, please enter the format of signals from this group:")
        context.user_data["waiting_for_signal_format"] = True

# ✅ Function: Collect Signal Format
async def collect_signal_format(update: Update, context: CallbackContext) -> None:
    """Receives the signal format and confirms subscription."""
    if context.user_data.get("waiting_for_signal_format"):
        await update.message.delete()
        signal_format = update.message.text.strip()

        if not signal_format:
            await update.message.reply_text("⚠️ Invalid input! Please enter a valid signal format.")
            return

        group_link = context.user_data.get("group_link", "Not provided")
        del context.user_data["waiting_for_signal_format"]

        context.user_data["signal_data"] = {"group_link": group_link, "signal_format": signal_format}

        keyboard = [[InlineKeyboardButton("✅ Subscribe", callback_data="subscribe")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"✅ Format saved!\n\n🔗 *Group Link:* {group_link}\n📊 *Signal Format:* {signal_format}\n\nClick 'Subscribe' to start receiving signals.", parse_mode="Markdown", reply_markup=reply_markup)

# ✅ Function: Subscribe User
async def subscribe_user(update: Update, context: CallbackContext) -> None:
    """Handles subscription by sending data to API."""
    query = update.callback_query
    await query.message.delete()
    user_id = query.from_user.id

    signal_data = context.user_data.get("signal_data", {})

    if not signal_data:
        await query.answer("❌ No subscription data found. Please enter your group link and signal format first.")
        return

    group_link = signal_data.get("group_link")
    signal_format = signal_data.get("signal_format")

    data = {"user_id": user_id, "group_link": group_link, "signal_format": signal_format}
    
    response = requests.post(f"{API_URL}/subscribe", json=data)

    if response.status_code == 200:
        await query.answer("✅ Subscription successful!")
        await query.message.reply_text("✅ You have successfully subscribed!")
    else:
        await query.answer("❌ Subscription failed. Try again.")

# ✅ Function: Show Subscribed Groups
async def show_subscribed_groups(update: Update, context: CallbackContext) -> None:
    """Shows the user's subscribed groups."""
    query = update.callback_query
    await query.message.delete()
    user_id = query.from_user.id

    response = requests.post(f"{API_URL}/get_subscriptions", json={"user_id": user_id})
    data = response.json()

    if "subscriptions" in data and data["subscriptions"]:
        message = "📋 *Your Active Copy Signals:*\n\n"
        keyboard = []
        for group_id, group_link, signal_format in data["subscriptions"]:
            message += f"🔗 [{group_id}]({group_link}) - *{signal_format}*\n"
            keyboard.append([InlineKeyboardButton(f"❌ Remove {group_id}", callback_data=f"unsubscribe:{group_id}")])
        
        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="copy_telegram")])  # ✅ FIXED
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await query.message.reply_text("⚠️ You have no active subscriptions.", parse_mode="Markdown")
