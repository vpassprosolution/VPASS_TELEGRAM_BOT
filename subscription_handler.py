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
    
    response = requests.post(API_SUBSCRIBE, json=payload)

    if response.status_code == 200:
        update.message.reply_text("✅ You are now subscribed to VPASS signals!")
    elif response.status_code == 400:
        update.message.reply_text("⚠️ You are already subscribed.")
    else:
        update.message.reply_text("❌ Subscription failed. Please try again.")

def unsubscribe(update: Update, context: CallbackContext) -> None:
    """Unsubscribe the user from receiving signals."""
    chat_id = update.message.chat_id
    payload = {"chat_id": chat_id}

    response = requests.post(API_UNSUBSCRIBE, json=payload)

    if response.status_code == 200:
        update.message.reply_text("🚫 You have unsubscribed from VPASS signals.")
    else:
        update.message.reply_text("❌ Unsubscription failed. Please try again.")

