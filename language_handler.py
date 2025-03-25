from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import connect_db


def save_user_language(user_id, language_code):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET language = %s WHERE user_id = %s", (language_code, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_user_language(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT language FROM users WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result and result[0]:
        return result[0]
    else:
        return "en"


# Show Language Selection Menu
async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")],
    [InlineKeyboardButton("🇲🇾 Bahasa Melayu", callback_data="set_lang_ms")],
    [InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="set_lang_id")],
    [InlineKeyboardButton("🇹🇭 ภาษาไทย", callback_data="set_lang_th")],
    [InlineKeyboardButton("🇨🇳 中文", callback_data="set_lang_zh")],
    [InlineKeyboardButton("🇮🇳 हिंदी", callback_data="set_lang_hi")],
    [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
])

    await query.message.edit_text("🌍 Please select your language:", reply_markup=keyboard)

# Handle Language Selection & Confirmation
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang_code = query.data.replace("set_lang_", "")

    save_user_language(user_id, lang_code)
    await query.answer("✅ Language updated!")

    # Show translated confirmation + back to menu
    message = get_text(user_id, "language_saved")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]
    ])
    await query.message.edit_text(message, reply_markup=keyboard)

# Translations Dictionary
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
    "btn_signal": {
        "en": "VESSA AI SMART SIGNAL",
        "ms": "ISYARAT PINTAR VESSA AI",
        "id": "SINYAL PINTAR VESSA AI",
        "th": "สัญญาณอัจฉริยะ VESSA AI",
        "zh": "VESSA AI 智能信号",
        "hi": "VESSA AI स्मार्ट सिग्नल"
    },
    "btn_sentiment": {
        "en": "VESSA AI SENTIMENT",
        "ms": "SENTIMEN VESSA AI",
        "id": "SENTIMEN VESSA AI",
        "th": "ความรู้สึก VESSA AI",
        "zh": "VESSA AI 情绪分析",
        "hi": "VESSA AI सेंटीमेंट"
    },
    "btn_technical": {
        "en": "VESSA AI TECHNICAL ANALYSIS",
        "ms": "ANALISIS TEKNIKAL VESSA AI",
        "id": "ANALISIS TEKNIKAL VESSA AI",
        "th": "วิเคราะห์ทางเทคนิค VESSA AI",
        "zh": "VESSA AI 技术分析",
        "hi": "VESSA AI तकनीकी विश्लेषण"
    },
    "btn_instant": {
        "en": "AI AGENT INSTANT SIGNAL",
        "ms": "ISYARAT SEGERA AI",
        "id": "SINYAL INSTAN AI",
        "th": "สัญญาณด่วนจาก AI",
        "zh": "AI 即时信号",
        "hi": "AI एजेंट इंस्टेंट सिग्नल"
    },
    "btn_news": {
        "en": "📰 NEWS",
        "ms": "📰 BERITA",
        "id": "📰 BERITA",
        "th": "📰 ข่าว",
        "zh": "📰 新闻",
        "hi": "📰 समाचार"
    },
    "btn_news_war_room": {
        "en": "🔥 NEWS WAR ROOM 🔥",
        "ms": "🔥 BILIK PERANG BERITA 🔥",
        "id": "🔥 RUANG PERANG BERITA 🔥",
        "th": "🔥 ห้องข่าวร้อน 🔥",
        "zh": "🔥 新闻作战室 🔥",
        "hi": "🔥 न्यूज़ वॉर रूम 🔥"
    },
    "btn_language": {
        "en": "🌍 Language",
        "ms": "🌍 Bahasa",
        "id": "🌍 Bahasa",
        "th": "🌍 ภาษา",
        "zh": "🌍 语言",
        "hi": "🌍 भाषा"
    },
"smart_signal_title": {
    "en": "*Select Your Exclusive Instrument*",
    "ms": "*Pilih Instrumen Eksklusif Anda*",
    "id": "*Pilih Instrumen Eksklusif Anda*",
    "th": "*เลือกสินทรัพย์ที่คุณต้องการ*",
    "zh": "*选择您的专属交易品种*",
    "hi": "*अपना एक्सक्लूसिव इंस्ट्रूमेंट चुनें*"
},
"btn_back": {
    "en": "🔙 Back",
    "ms": "🔙 Kembali",
    "id": "🔙 Kembali",
    "th": "🔙 ย้อนกลับ",
    "zh": "🔙 返回",
    "hi": "🔙 वापस"
},
"subscribe_to": {
    "en": "✅ Subscribe to {instrument}",
    "ms": "✅ Langgan {instrument}",
    "id": "✅ Berlangganan {instrument}",
    "th": "✅ รับสัญญาณ {instrument}",
    "zh": "✅ 订阅 {instrument}",
    "hi": "✅ {instrument} की सदस्यता लें"
},
"unsubscribe_from": {
    "en": "❌ Unsubscribe from {instrument}",
    "ms": "❌ Berhenti langganan {instrument}",
    "id": "❌ Berhenti berlangganan {instrument}",
    "th": "❌ ยกเลิกสัญญาณ {instrument}",
    "zh": "❌ 取消订阅 {instrument}",
    "hi": "❌ {instrument} की सदस्यता रद्द करें"
},
"sub_success": {
    "en": "✅ You are now subscribed to {instrument} alerts!",
    "ms": "✅ Anda telah melanggan amaran {instrument}!",
    "id": "✅ Anda telah berlangganan sinyal {instrument}!",
    "th": "✅ คุณได้สมัครรับการแจ้งเตือน {instrument} แล้ว!",
    "zh": "✅ 您已订阅 {instrument} 警报！",
    "hi": "✅ आपने {instrument} अलर्ट की सदस्यता ले ली है!"
},
"sub_failed": {
    "en": "❌ Subscription failed for {instrument}. Try again.",
    "ms": "❌ Gagal melanggan {instrument}. Cuba lagi.",
    "id": "❌ Gagal berlangganan {instrument}. Coba lagi.",
    "th": "❌ ไม่สามารถสมัครสมาชิก {instrument} ได้ กรุณาลองใหม่",
    "zh": "❌ 订阅 {instrument} 失败。请再试一次。",
    "hi": "❌ {instrument} की सदस्यता असफल रही। कृपया पुनः प्रयास करें।"
},
"unsub_success": {
    "en": "🚫 You have unsubscribed from {instrument} alerts.",
    "ms": "🚫 Anda telah berhenti melanggan amaran {instrument}.",
    "id": "🚫 Anda telah berhenti berlangganan sinyal {instrument}.",
    "th": "🚫 คุณได้ยกเลิกการแจ้งเตือน {instrument} แล้ว",
    "zh": "🚫 您已取消订阅 {instrument} 警报。",
    "hi": "🚫 आपने {instrument} की सदस्यता रद्द कर दी है।"
},
"unsub_failed": {
    "en": "❌ Unsubscription failed for {instrument}. Try again.",
    "ms": "❌ Gagal berhenti melanggan {instrument}. Cuba lagi.",
    "id": "❌ Gagal berhenti berlangganan {instrument}. Coba lagi.",
    "th": "❌ ยกเลิกการสมัคร {instrument} ล้มเหลว กรุณาลองใหม่",
    "zh": "❌ 取消订阅 {instrument} 失败。请再试一次。",
    "hi": "❌ {instrument} की सदस्यता रद्द करने में विफल। फिर से प्रयास करें।"
}

}

# Get translated text for current user
def get_text(user_id, key):
    lang = get_user_language(user_id)
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("en", key))
