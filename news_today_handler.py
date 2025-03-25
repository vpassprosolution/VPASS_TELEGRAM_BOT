import httpx
import base64

NEWS_API_URL = "https://vpassnewstoday-production.up.railway.app/get_today_news"

async def handle_news_today(bot, call):
    await safe_replace_message(bot, call, "📰 Fetching today’s news...")

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(NEWS_API_URL, timeout=15)
            data = res.json()

        if data["status"] != "success":
            await safe_replace_message(bot, call, "⚠️ No news found today.")
            return

        news_text = data["news_text"]
        image_bytes = bytes.fromhex(data["image_base64"])

        await bot.send_photo(chat_id=call.message.chat.id, photo=image_bytes, caption=news_text)

    except Exception as e:
        print("❌ Error in news handler:", e)
        await safe_replace_message(bot, call, "⚠️ Something went wrong. Please try again later.")

# 🔁 Util function to safely replace message (like your flood-safe bot)
async def safe_replace_message(bot, call, new_text):
    try:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=new_text)
    except:
        await bot.send_message(chat_id=call.message.chat.id, text=new_text)
