import re
import random
from telegram import Bot

# Store OTPs temporarily
phone_verification_codes = {}

def validate_phone_number(phone_number):
    """Check if the phone number is valid (must start with + and contain only digits)"""
    pattern = r"^\+\d{7,15}$"  # ✅ Matches +123456789 (7-15 digits)
    return re.match(pattern, phone_number) is not None

def generate_otp():
    """Generate a random 6-digit OTP"""
    return random.randint(100000, 999999)

async def send_telegram_otp(context, user_id):
    """Send OTP via Telegram message to the user's chat ID"""
    import random

    otp_code = random.randint(100000, 999999)
    phone_verification_codes[user_id] = otp_code  # ✅ Store OTP linked to user ID

    bot = context.bot  # Get bot instance
    try:
        # ✅ Send OTP as a Telegram message to the user (NOT to phone number)
        await bot.send_message(
            chat_id=user_id,  # Use `user_id` (chat_id) instead of `phone_number`
            text=f"🔑 Your VPASS PRO verification code is: {otp_code}\n"
                 "Please enter this code in the bot to verify your phone number."
        )
        return True  # ✅ OTP sent successfully
    except Exception as e:
        print(f"❌ Failed to send OTP via Telegram: {e}")
        return False  # ❌ OTP failed to send


async def verify_otp(phone_number, user_input):
    """Check if the entered OTP is correct"""
    if phone_number in phone_verification_codes:
        if str(user_input) == str(phone_verification_codes[phone_number]):
            del phone_verification_codes[phone_number]  # ✅ Remove OTP after successful verification
            return True  # ✅ OTP is correct
        else:
            return False  # ❌ OTP is incorrect

    return None  # ❌ No OTP found
