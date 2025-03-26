from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

async def social_media(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🚀 Telegram", url="https://t.me/vessacommunity")],
        [
            InlineKeyboardButton("📘 Facebook", url="https://www.facebook.com/vessaproai"),
            InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/vessaproai/")
        ],
        [
            InlineKeyboardButton("🐦 Twitter", url="https://x.com/vessaproai"),
            InlineKeyboardButton("🎵 TikTok", url="https://www.tiktok.com/@vessaproai")
        ],
        [
            InlineKeyboardButton("▶️ YouTube", url="https://www.youtube.com/@Vessaproai"),
            InlineKeyboardButton("💼 LinkedIn", url="https://www.linkedin.com")  # update if you have specific URL
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
        "🌐 <b>Join our social media platforms!</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
