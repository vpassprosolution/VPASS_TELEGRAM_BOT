from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils import safe_replace_message  # make sure this exists in your project

# ===== In-memory storage =====
user_mt5_steps = {}
user_risk_steps = {}  # ✅ Add this line to fix the error





async def auto_copy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📥 Link My MT5 Account", callback_data="link_mt5")],
        [InlineKeyboardButton("⚙️ Set Risk Preference", callback_data="risk_setting")],
        [InlineKeyboardButton("💎 Upgrade to Premium", callback_data="upgrade_premium")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
    ]

    await safe_replace_message(
        query,
        context,
        text="🚀 *MT5 Auto Copy Menu*\n\nSet up your MT5 account and preferences below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def link_mt5_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()
    await query.message.delete()

    user_mt5_steps[user_id] = {"step": "broker"}
    sent = await query.message.reply_text("📍 Enter your MT5 broker name:")
    user_mt5_steps[user_id]["message_id"] = sent.message_id


async def risk_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()
    await query.message.delete()

    user_risk_steps[user_id] = {"step": "method"}
    
    keyboard = [
        [InlineKeyboardButton("📏 Fixed Lot Size", callback_data="risk_fixed")],
        [InlineKeyboardButton("📊 Risk % of Balance", callback_data="risk_percent")],
        [InlineKeyboardButton("⬅️ Back", callback_data="auto_copy")]
    ]

    msg = await query.message.reply_text(
        "⚙️ *Select your risk method:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    user_risk_steps[user_id]["message_id"] = msg.message_id

async def set_fixed_lot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()
    await query.message.delete()

    user_risk_steps[user_id]["method"] = "fixed"
    user_risk_steps[user_id]["step"] = "fixed_lot"

    msg = await query.message.reply_text("✏️ Enter fixed lot size (e.g., 0.01):")
    user_risk_steps[user_id]["message_id"] = msg.message_id


async def set_risk_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()
    await query.message.delete()

    user_risk_steps[user_id]["method"] = "percent"
    user_risk_steps[user_id]["step"] = "risk_percent"

    msg = await query.message.reply_text("✏️ Enter risk % of account (e.g., 2):")
    user_risk_steps[user_id]["message_id"] = msg.message_id

async def confirm_risk_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in user_risk_steps:
        await query.message.edit_text("❌ Something went wrong. Try again.")
        return

    method = user_risk_steps[user_id]["method"]
    value = user_risk_steps[user_id]["value"]

    # 🔒 Later, send this to backend API

    del user_risk_steps[user_id]

    await query.message.edit_text(
        f"✅ Your risk preference has been saved:\n\n"
        f"Method: {method}\nValue: {value}"
    )





async def upgrade_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💎 This feature is only for Premium Members.\n\nPayment system coming soon!"
    )

async def collect_mt5_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_mt5_steps:
        return

    step = user_mt5_steps[user_id]["step"]

    # ✅ Delete user message + last bot message
    try:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=user_mt5_steps[user_id]["message_id"])
    except:
        pass

    if step == "broker":
        user_mt5_steps[user_id]["broker"] = text
        user_mt5_steps[user_id]["step"] = "login"
        msg = await update.message.reply_text("🔐 Enter your MT5 Login ID:")
        user_mt5_steps[user_id]["message_id"] = msg.message_id

    elif step == "login":
        user_mt5_steps[user_id]["login"] = text
        user_mt5_steps[user_id]["step"] = "password"
        msg = await update.message.reply_text("🔑 Enter your MT5 Password:")
        user_mt5_steps[user_id]["message_id"] = msg.message_id

    elif step == "password":
        user_mt5_steps[user_id]["password"] = text
        user_mt5_steps[user_id]["step"] = "confirm"

        broker = user_mt5_steps[user_id]["broker"]
        login = user_mt5_steps[user_id]["login"]
        password = text

        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm_mt5_login")],
            [InlineKeyboardButton("🔁 Start Over", callback_data="link_mt5")]
        ]

        msg = await update.message.reply_text(
            f"📥 *Your MT5 Details:*\n"
            f"📍 Broker: `{broker}`\n"
            f"🔐 Login ID: `{login}`\n"
            f"🔑 Password: `{password}`\n\n"
            f"Do you want to confirm?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        user_mt5_steps[user_id]["message_id"] = msg.message_id

async def collect_risk_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_risk_steps:
        return

    step = user_risk_steps[user_id]["step"]

    try:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=user_risk_steps[user_id]["message_id"])
    except:
        pass

    if step == "fixed_lot":
        user_risk_steps[user_id]["value"] = text
        method = user_risk_steps[user_id]["method"]
        value = text

        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm_risk_setting")],
            [InlineKeyboardButton("🔁 Start Over", callback_data="risk_setting")]
        ]

        msg = await update.message.reply_text(
            f"⚙️ Risk Method: `{method}`\n"
            f"📏 Value: `{value}`\n\n"
            f"Confirm your setting?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        user_risk_steps[user_id]["message_id"] = msg.message_id

    elif step == "risk_percent":
        user_risk_steps[user_id]["value"] = text
        method = user_risk_steps[user_id]["method"]
        value = text

        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm_risk_setting")],
            [InlineKeyboardButton("🔁 Start Over", callback_data="risk_setting")]
        ]

        msg = await update.message.reply_text(
            f"⚙️ Risk Method: `{method}`\n"
            f"📊 Value: `{value}%`\n\n"
            f"Confirm your setting?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        user_risk_steps[user_id]["message_id"] = msg.message_id


async def confirm_mt5_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in user_mt5_steps:
        await query.message.edit_text("❌ Something went wrong. Start again.")
        return

    data = user_mt5_steps[user_id]
    broker = data["broker"]
    login = data["login"]
    password = data["password"]

    # 🧠 Here later you will send data to backend via API

    del user_mt5_steps[user_id]  # ✅ Clear temp storage

    await query.message.edit_text(
        "✅ Your MT5 login details have been recorded!\n\n(We will connect to MetaAPI after surface is done.)"
    )
