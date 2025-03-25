import httpx
import base64
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

NEWS_API_URL = "https://vpassnewstoday-production.up.railway.app/get_today_news"

async def handle_news_today(update, context):
    await safe_replace_message(update, context, "📰 Fetching today’s news...")

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(NEWS_API_URL, timeout=15)
            data = res.json()

        if data["status"] != "success":
            await safe_replace_message(update, context, "⚠️ No news found today.")
            return

        news_text = data["news_text"]
        image_bytes = bytes.fromhex(data["image_base64"])

        # Add inline F.Factory button under the image
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("F.Factory", url="https://www.forexfactory.com")]
        ])

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=image_bytes,
            caption=news_text,
            reply_markup=markup
        )

    except Exception as e:
        print("❌ Error in news handler:", e)
        await safe_replace_message(update, context, "⚠️ Something went wrong. Please try again later.")

# ✅ Safe message replace for async telegram.ext
async def safe_replace_message(update, context, new_text):
    try:
        await update.callback_query.edit_message_text(text=new_text)
    except Exception:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=new_text)
