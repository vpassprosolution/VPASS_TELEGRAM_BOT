import re
import random
from telegram import Bot

# Store OTPs temporarily (linked to `user_id`)
phone_verification_codes = {}

def validate_phone_number(phone_number):
    """Check if the phone number is valid (must start with + and contain only digits)"""
    pattern = r"^\+\d{7,15}$"  # ✅ Matches +123456789 (7-15 digits)
    return re.match(pattern, phone_number) is not None

def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))  # ✅ Ensure OTP is a string for proper comparison

async def send_telegram_otp(context, user_id):
    """Send OTP via Telegram message to the user's chat ID"""

    otp_code = generate_otp()
    phone_verification_codes[user_id] = otp_code  # ✅ Store OTP linked to `user_id`

    bot = context.bot  # Get bot instance
    try:
        # ✅ Send OTP as a Telegram message to the user (NOT to phone number)
        await bot.send_message(
            chat_id=user_id,  # Use `user_id` (chat_id) instead of `phone_number`
            text=f"🔑 Your VPASS PRO verification code is: {otp_code}\n"
                 "Please enter this code in the bot to verify your phone number."
        )
        print(f"✅ DEBUG: OTP sent to user {user_id}: {otp_code}")  # Debugging log
        return True  # ✅ OTP sent successfully
    except Exception as e:
        print(f"❌ Failed to send OTP via Telegram: {e}")
        return False  # ❌ OTP failed to send


async def verify_otp(user_id, user_input):
    """Check if the entered OTP is correct"""
    stored_otp = phone_verification_codes.get(user_id)  # ✅ Get stored OTP using `user_id`
    
    if stored_otp and user_input.strip() == stored_otp.strip():
        del phone_verification_codes[user_id]  # ✅ Remove OTP after successful verification
        print(f"✅ DEBUG: OTP verified successfully for user {user_id}")
        return True  # ✅ OTP is correct
    else:
        print(f"❌ DEBUG: Incorrect OTP entered by user {user_id}. Expected: {stored_otp}, Got: {user_input}")
        return False  # ❌ OTP is incorrect
