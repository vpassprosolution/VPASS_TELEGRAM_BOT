import requests
from telegram import Update
from telegram.ext import CallbackContext

# Webhook API URLs
API_SUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/subscribe"
API_UNSUBSCRIBE = "https://vpasstradingviewwebhook-production.up.railway.app/unsubscribe"

def subscribe(update: Update, context: CallbackContext) -> None:
    """Subscribe the user to signals."""
    chat_id = update.message.chat_id
    payload = {"chat_id": chat_id}
    
    try:
        response = requests.post(API_SUBSCRIBE, json=payload)
        response_json = response.json()

        if response.status_code == 200:
            update.message.reply_text(f"✅ {response_json.get('message', 'Subscription successful!')}")
        elif response.status_code == 400:
            update.message.reply_text("⚠️ You are already subscribed.")
        else:
            update.message.reply_text(f"❌ Subscription failed. Response: {response.text}")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def unsubscribe(update: Update, context: CallbackContext) -> None:
    """Unsubscribe the user from receiving signals."""
    chat_id = update.message.chat_id
    payload = {"chat_id": chat_id}

    try:
        response = requests.post(API_UNSUBSCRIBE, json=payload)
        response_json = response.json()

        if response.status_code == 200:
            update.message.reply_text(f"🚫 {response_json.get('message', 'Unsubscription successful!')}")
        else:
            update.message.reply_text(f"❌ Unsubscription failed. Response: {response.text}")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")
