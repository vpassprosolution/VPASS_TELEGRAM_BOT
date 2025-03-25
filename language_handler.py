import json
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

LANGUAGE_FILE = "user_languages.json"

# Save language to file
def save_user_language(user_id, language_code):
    try:
        with open(LANGUAGE_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data[str(user_id)] = language_code

    with open(LANGUAGE_FILE, "w") as f:
        json.dump(data, f)

# Get user language
def get_user_language(user_id):
    try:
        with open(LANGUAGE_FILE, "r") as f:
            data = json.load(f)
        return data.get(str(user_id), "en")
    except FileNotFoundError:
        return "en"

# Language Selection Menu
async def show_language_menu(callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🇲🇾 Bahasa Melayu", callback_data="set_lang_ms")],
        [InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="set_lang_id")],
        [InlineKeyboardButton("🇹🇭 ภาษาไทย", callback_data="set_lang_th")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data="set_lang_zh")],
        [InlineKeyboardButton("🇮🇳 हिंदी", callback_data="set_lang_hi")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    await callback_query.message.edit_text("🌍 Please select your language:", reply_markup=keyboard)

# Handle Language Selection
async def set_language(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = callback_query.data.replace("set_lang_", "")  # e.g., 'ms'

    save_user_language(user_id, lang_code)

    await callback_query.answer("✅ Language updated!")
    await callback_query.message.edit_text("✅ Your language preference has been saved.")

# Dictionary with translations
translations = {
    "main_menu_title": {
        "en": "WELCOME TO VESSA PRO VERSION V2\n   The Future of Intelligence Starts Here\n          CHOOSE YOUR STRATEGY",
        "ms": "SELAMAT DATANG KE VESSA PRO VERSI V2\n   Masa Depan Kecerdasan Bermula Di Sini\n          PILIH STRATEGI ANDA",
        "id": "SELAMAT DATANG DI VESSA PRO VERSI V2\n   Masa Depan Kecerdasan Dimulai Di Sini\n          PILIH STRATEGI ANDA",
        "th": "ยินดีต้อนรับสู่ VESSA PRO V2\n   อนาคตแห่งความฉลาดเริ่มต้นที่นี่\n          เลือกกลยุทธ์ของคุณ",
        "zh": "欢迎使用 VESSA PRO V2\n   智能的未来从这里开始\n          选择你的策略",
        "hi": "VESSA PRO संस्करण V2 में आपका स्वागत है\n   बुद्धिमत्ता का भविष्य यहाँ से शुरू होता है\n          अपनी रणनीति चुनें"
    },
    "language_saved": {
        "en": "✅ Your language preference has been saved.",
        "ms": "✅ Bahasa pilihan anda telah disimpan.",
        "id": "✅ Bahasa pilihan Anda telah disimpan.",
        "th": "✅ การตั้งค่าภาษาของคุณถูกบันทึกแล้ว",
        "zh": "✅ 您的语言偏好已保存。",
        "hi": "✅ आपकी भाषा वरीयता सहेज ली गई है।"
    },
    # You can add more keys here later...
}

# Get translated text
def get_text(user_id, key):
    lang = get_user_language(user_id)
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("en", key))
