import requests

# Bot token and Telegram channel details
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"
CHANNEL_ID = "@vessacommunity"  # Use the channel username, NOT the ID

def is_user_in_channel(user_id):
    """
    Check if a user is a member of the Telegram channel.
    Returns True if they are in the channel, otherwise False.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    response = requests.get(url).json()

    if response.get("ok"):
        status = response["result"]["status"]
        if status in ["member", "administrator", "creator"]:
            return True  # ✅ User is in the channel
    return False  # ❌ User is NOT in the channel
