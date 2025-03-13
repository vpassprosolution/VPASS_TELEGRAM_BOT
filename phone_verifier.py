import random

# Temporary storage for OTPs
phone_verification_codes = {}

def generate_otp():
    """Generate a random 6-digit OTP"""
    return random.randint(100000, 999999)

async def get_telegram_phone(update, context):
    """Try to get the user's phone number from Telegram"""
    user_id = update.message.from_user.id

    try:
        # Try fetching user details
        user_info = await context.bot.get_chat(user_id)

        # Check if Telegram provides a phone number
        if hasattr(user_info, "phone_number") and user_info.phone_number:
            return user_info.phone_number  # ✅ Telegram provided the phone number
        else:
            return None  # ❌ Telegram did NOT provide a phone number

    except Exception as e:
        print(f"❌ Error fetching phone number: {e}")
        return None

async def send_telegram_otp(update, context, phone_number):
    """Send OTP to the user's Telegram chat"""
    user_id = update.message.from_user.id

    # Generate OTP
    otp_code = generate_otp()
    phone_verification_codes[user_id] = otp_code

    # Send OTP message in Telegram
    await update.message.reply_text(
        f"📩 Your VPASS PRO verification code is: {otp_code}\n"
        "Please enter this code in the bot to verify your phone number."
    )

async def verify_otp(update, context):
    """Verify the OTP entered by the user"""
    user_id = update.message.from_user.id
    user_input = update.message.text

    if user_id in phone_verification_codes:
        if int(user_input) == phone_verification_codes[user_id]:
            del phone_verification_codes[user_id]  # Remove OTP after verification
            return True  # ✅ OTP is correct
        else:
            return False  # ❌ Incorrect OTP

    return None  # No OTP found
