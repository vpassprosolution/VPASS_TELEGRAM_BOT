from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# ⚙️ SETUP MENU
async def setup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("🌐 Language", callback_data="language_menu"),
            InlineKeyboardButton("🎓 Tutorial", callback_data="coming_soon")
        ],
        [
            InlineKeyboardButton("💬 Live Chat", callback_data="live_chat"),
            InlineKeyboardButton("🛠️ Support", url="https://t.me/vpassprosupport")
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]

    await query.message.edit_text(
        "⚙️CHOOSE YOUR SETUP MENU⚙️",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🚧 COMING SOON
async def coming_soon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "🚧 This feature is coming soon!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="setup_menu")]])
    )
