import httpx
import base64
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


# 🌐 API Endpoint
NEWS_API_URL = "https://vpassnewstoday-production.up.railway.app/get_today_news"


# 📰 Handle Today's News Feature
async def handle_news_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # 🧹 Clean main menu message
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except:
        pass

    # ⏳ Show loading
    loading = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="📰 Fetching today’s news..."
    )

    try:
        # 🔗 API Call
        async with httpx.AsyncClient() as client:
            res = await client.get(NEWS_API_URL, timeout=15)
            data = res.json()

        # ❌ If failed or no news
        if data.get("status") != "success":
            await context.bot.edit_message_text(
                chat_id=loading.chat_id,
                message_id=loading.message_id,
                text="⚠️ No high-impact news today."
            )
            return

        # ✅ Decode & prepare content
        news_text = data.get("news_text", "⚠️ No text found.")
        image_base64 = data.get("image_base64", "")

        if not image_base64:
            raise ValueError("Missing base64 image data from API.")

        image_bytes = base64.b64decode(image_base64)

        # 🧹 Delete loading
        await context.bot.delete_message(chat_id=loading.chat_id, message_id=loading.message_id)

        # 📎 Buttons
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu"),
                InlineKeyboardButton("🌐 F.Factory", url="https://www.forexfactory.com")
            ]
        ])

        # 🖼 Send image + caption + buttons
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image_bytes,
            caption=news_text,
            reply_markup=buttons
        )

    except Exception as e:
        print(f"❌ NEWS ERROR: {e}")
        try:
            await context.bot.edit_message_text(
                chat_id=loading.chat_id,
                message_id=loading.message_id,
                text="⚠️ Something went wrong. Please try again later."
            )
        except:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="⚠️ Something went wrong. Please try again later."
            )
