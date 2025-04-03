from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils import safe_replace_message
from language_handler import get_text

# ✅ This handles the main menu layout and display

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # ✅ Trigger language cache for this user (if not already)
    _ = get_text(user_id, "main_menu_title", context)

    # ✅ Use shorthand getter for fast cached access
    get = lambda key: get_text(user_id, key, context)

    keyboard = [
        [InlineKeyboardButton(get("btn_signal"), callback_data="vpass_smart_signal")],
        [InlineKeyboardButton(get("btn_sentiment"), callback_data="ai_sentiment")],
        [InlineKeyboardButton(get("btn_technical"), callback_data="ai_technical")],
        [InlineKeyboardButton(get("btn_instant"), callback_data="ai_agent_signal")],
        [InlineKeyboardButton("\ud83d\ude80 AUTO COPY TO MT5", callback_data="auto_copy")],
        [
            InlineKeyboardButton(get("btn_news"), callback_data="news_today"),
            InlineKeyboardButton("\ud83d\udcf1 MEDIA", callback_data="social_media"),
            InlineKeyboardButton("\u2699\ufe0f SETUP", callback_data="setup_menu")
        ]
    ]

    await safe_replace_message(
        query,
        context,
        text=get("main_menu_title"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
