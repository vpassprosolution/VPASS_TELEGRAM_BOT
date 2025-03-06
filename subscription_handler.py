import requests
from telegram import Update
from telegram.ext import CallbackContext

# Webhook API URLs
API_SUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/subscribe"
API_UNSUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/unsubscribe"

async def subscribe(update: Update, context: CallbackContext) -> None:
    """Subscribe the user to signals."""
    chat_id = update.message.chat_id
    payload = {"chat_id": chat_id}

    await update.message.reply_text("🛠 Debug: Sending subscription request...")

    try:
        response = requests.post(API_SUBSCRIBE, json=payload)
        response_json = response.json()

        if response.status_code == 200:
            await update.message.reply_text(f"✅ {response_json.get('message', 'Subscription successful!')}")
        elif response.status_code == 400:
            await update.message.reply_text("⚠️ You are already subscribed.")
        else:
            await update.message.reply_text(f"❌ Subscription failed. Debug Response: {response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def unsubscribe(update: Update, context: CallbackContext) -> None:
    """Unsubscribe the user from receiving signals."""
    chat_id = update.message.chat_id
    payload = {"chat_id": chat_id}

    await update.message.reply_text("🛠 Debug: Sending unsubscription request...")

    try:
        response = requests.post(API_UNSUBSCRIBE, json=payload)
        response_json = response.json()

        if response.status_code == 200:
            await update.message.reply_text(f"🚫 {response_json.get('message', 'Unsubscription successful!')}")
        else:
            await update.message.reply_text(f"❌ Unsubscription failed. Debug Response: {response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
