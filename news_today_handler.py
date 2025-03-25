import httpx
import base64
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

NEWS_API_URL = "https://vpassnewstoday-production.up.railway.app/get_today_news"

async def handle_news_today(update, context):
    query = update.callback_query
    await query.answer()

    # 🧹 Delete the main menu message
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception:
        pass

    # 🕒 Show "Fetching news..." message
    loading_msg = await context.bot.send_message(
        chat_id=query.message.chat_id,
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

        # 📰 News is ready
        news_text = data["news_text"]
        image_bytes = bytes.fromhex(data["image_base64"])

        # 🧹 Delete the "Fetching..." message
        await context.bot.delete_message(chat_id=loading_msg.chat_id, message_id=loading_msg.message_id)

        # 📎 Buttons: Back + F.Factory
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu"),
             InlineKeyboardButton("🌐 F.Factory", url="https://www.forexfactory.com")]
        ])

        # 🖼 Send image + text + buttons
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image_bytes,
            caption=news_text,
            reply_markup=buttons
        )

    except Exception as e:
        print("❌ Error in NEWS:", e)
        try:
            await context.bot.edit_message_text(
                chat_id=loading_msg.chat_id,
                message_id=loading_msg.message_id,
                text="⚠️ Something went wrong. Please try again later."
            )
        except:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="⚠️ Something went wrong. Please try again later."
            )
