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

async def send_telegram_otp(context, phone_number):
    """Send OTP via Telegram message to the user's phone number (outside the bot)"""
    otp_code = generate_otp()
    phone_verification_codes[phone_number] = otp_code  # ✅ Store OTP linked to phone number

    bot = context.bot  # Get bot instance
    try:
        # ✅ Send OTP as a direct Telegram message to the phone number
        await bot.send_message(
            chat_id=phone_number,  # Sending OTP to Telegram user associated with this number
            text=f"🔑 Your VPASS PRO verification code is: {otp_code}\n"
                 "Please enter this code in the bot to verify your phone number."
        )
        return True  # ✅ OTP sent successfully
    except Exception as e:
        print(f"❌ Failed to send OTP via Telegram to {phone_number}: {e}")
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
