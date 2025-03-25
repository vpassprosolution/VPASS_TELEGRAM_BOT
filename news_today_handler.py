import httpx
import base64
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

NEWS_API_URL = "https://vpassnewstoday-production.up.railway.app/get_today_news"

async def handle_news_today(update, context):
    # Step 1: Send temporary loading message
    loading_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📰 Fetching today’s news..."
    )

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(NEWS_API_URL, timeout=15)
            data = res.json()

        if data["status"] != "success":
            await context.bot.edit_message_text(
                chat_id=loading_msg.chat_id,
                message_id=loading_msg.message_id,
                text="⚠️ No news found today."
            )
            return

        news_text = data["news_text"]
        image_bytes = bytes.fromhex(data["image_base64"])

        # Step 2: Delete the loading message
        await context.bot.delete_message(chat_id=loading_msg.chat_id, message_id=loading_msg.message_id)

        # Step 3: Build buttons
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu"),
             InlineKeyboardButton("🌐 F.Factory", url="https://www.forexfactory.com")]
        ])

        # Step 4: Send the final news
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=image_bytes,
            caption=news_text,
            reply_markup=markup
        )

    except Exception as e:
        print("❌ Error in news handler:", e)
        try:
            await context.bot.edit_message_text(
                chat_id=loading_msg.chat_id,
                message_id=loading_msg.message_id,
                text="⚠️ Something went wrong. Please try again later."
            )
        except:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Something went wrong. Please try again later."
            )
