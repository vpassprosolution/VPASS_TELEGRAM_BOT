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

    # ✅ Save to DB
    save_user_language(user_id, lang_code)

    # ✅ Cache in memory
    context.user_data["user_lang"] = lang_code

    await query.answer("✅ Language updated!")

    # ✅ Use cached version for fast response
    message = get_text(user_id, "language_saved", context)
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
        "en": "NAOMI ASSIST (INSTANT SIGNAL)",
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
},
# Instrument Names
"instrument_gold": {
    "en": "🏆 GOLD (XAUUSD)",
    "ms": "🏆 EMAS (XAUUSD)",
    "id": "🏆 EMAS (XAUUSD)",
    "th": "🏆 ทองคำ (XAUUSD)",
    "zh": "🏆 黄金 (XAUUSD)",
    "hi": "🏆 सोना (XAUUSD)"
},
"instrument_bitcoin": {
    "en": "₿ BITCOIN (BTC)",
    "ms": "₿ BITCOIN (BTC)",
    "id": "₿ BITCOIN (BTC)",
    "th": "₿ บิทคอยน์ (BTC)",
    "zh": "₿ 比特币 (BTC)",
    "hi": "₿ बिटकॉइन (BTC)"
},
"instrument_ethereum": {
    "en": "🪙 ETHEREUM (ETH)",
    "ms": "🪙 ETHEREUM (ETH)",
    "id": "🪙 ETHEREUM (ETH)",
    "th": "🪙 อีเธอเรียม (ETH)",
    "zh": "🪙 以太坊 (ETH)",
    "hi": "🪙 एथेरियम (ETH)"
},
"instrument_dowjones": {
    "en": "📈 DOW JONES (DJI)",
    "ms": "📈 DOW JONES (DJI)",
    "id": "📈 DOW JONES (DJI)",
    "th": "📈 ดาวโจนส์ (DJI)",
    "zh": "📈 道琼斯 (DJI)",
    "hi": "📈 डॉव जोन्स (DJI)"
},
"instrument_nasdaq": {
    "en": "📊 NASDAQ (IXIC)",
    "ms": "📊 NASDAQ (IXIC)",
    "id": "📊 NASDAQ (IXIC)",
    "th": "📊 แนสแด็ก (IXIC)",
    "zh": "📊 纳斯达克 (IXIC)",
    "hi": "📊 नैस्डैक (IXIC)"
},
"instrument_eurusd": {
    "en": "💶 EUR/USD (EURUSD)",
    "ms": "💶 EUR/USD (EURUSD)",
    "id": "💶 EUR/USD (EURUSD)",
    "th": "💶 ยูโร/ดอลลาร์ (EURUSD)",
    "zh": "💶 欧元/美元 (EURUSD)",
    "hi": "💶 यूरो/यूएसडी (EURUSD)"
},
"instrument_gbpusd": {
    "en": "💷 GBP/USD (GBPUSD)",
    "ms": "💷 GBP/USD (GBPUSD)",
    "id": "💷 GBP/USD (GBPUSD)",
    "th": "💷 ปอนด์/ดอลลาร์ (GBPUSD)",
    "zh": "💷 英镑/美元 (GBPUSD)",
    "hi": "💷 जीबीपी/यूएसडी (GBPUSD)"
},
"subscription_menu_title": {
    "en": "🔍 *{instrument} Subscription Menu:*",
    "ms": "🔍 *Menu Langganan {instrument}:*",
    "id": "🔍 *Menu Langganan {instrument}:*",
    "th": "🔍 *เมนูการสมัครสมาชิก {instrument}:*",
    "zh": "🔍 *{instrument} 订阅菜单：*",
    "hi": "🔍 *{instrument} सदस्यता मेनू:*"
},
"sentiment_title": {
    "en": "*Select Your Exclusive Instrument :*",
    "ms": "*Pilih Instrumen Eksklusif Anda :*",
    "id": "*Pilih Instrumen Eksklusif Anda :*",
    "th": "*เลือกสินทรัพย์ที่คุณต้องการ :*",
    "zh": "*选择您的专属交易品种：*",
    "hi": "*अपना एक्सक्लूसिव इंस्ट्रूमेंट चुनें :*"
},
"sentiment_back": {
    "en": "⬅️ Back to Menu",
    "ms": "⬅️ Kembali ke Menu",
    "id": "⬅️ Kembali ke Menu",
    "th": "⬅️ กลับไปยังเมนู",
    "zh": "⬅️ 返回菜单",
    "hi": "⬅️ मेनू पर वापस जाएं"
},
"instrument_gold": {
    "en": "🏆 GOLD (XAUUSD)",
    "ms": "🏆 EMAS (XAUUSD)",
    "id": "🏆 EMAS (XAUUSD)",
    "th": "🏆 ทองคำ (XAUUSD)",
    "zh": "🏆 黄金 (XAUUSD)",
    "hi": "🏆 सोना (XAUUSD)"
},
"instrument_bitcoin": {
    "en": "₿ BITCOIN (BTC)",
    "ms": "₿ BITCOIN (BTC)",
    "id": "₿ BITCOIN (BTC)",
    "th": "₿ บิทคอยน์ (BTC)",
    "zh": "₿ 比特币 (BTC)",
    "hi": "₿ बिटकॉइन (BTC)"
},
"instrument_ethereum": {
    "en": "🔣 ETHEREUM (ETH)",
    "ms": "🔣 ETHEREUM (ETH)",
    "id": "🔣 ETHEREUM (ETH)",
    "th": "🔣 อีเธอเรียม (ETH)",
    "zh": "🔣 以太坊 (ETH)",
    "hi": "🔣 एथेरियम (ETH)"
},
"instrument_dowjones": {
    "en": "📈 DOW JONES (DJI)",
    "ms": "📈 DOW JONES (DJI)",
    "id": "📈 DOW JONES (DJI)",
    "th": "📈 ดาวโจนส์ (DJI)",
    "zh": "📈 道琼斯 (DJI)",
    "hi": "📈 डॉव जोन्स (DJI)"
},
"instrument_nasdaq": {
    "en": "📊 NASDAQ (IXIC)",
    "ms": "📊 NASDAQ (IXIC)",
    "id": "📊 NASDAQ (IXIC)",
    "th": "📊 แนสแด็ก (IXIC)",
    "zh": "📊 纳斯达克 (IXIC)",
    "hi": "📊 नैस्डैक (IXIC)"
},
"instrument_eurusd": {
    "en": "💶 EUR/USD (EURUSD)",
    "ms": "💶 EUR/USD (EURUSD)",
    "id": "💶 EUR/USD (EURUSD)",
    "th": "💶 EUR/USD (EURUSD)",
    "zh": "💶 欧元/美元 (EURUSD)",
    "hi": "💶 यूरो/यूएसडी (EURUSD)"
},
"instrument_gbpusd": {
    "en": "💷 GBP/USD (GBPUSD)",
    "ms": "💷 GBP/USD (GBPUSD)",
    "id": "💷 GBP/USD (GBPUSD)",
    "th": "💷 GBP/USD (GBPUSD)",
    "zh": "💷 英镑/美元 (GBPUSD)",
    "hi": "💷 GBP/USD (GBPUSD)"
},
"sentiment_loading": {
    "en": "🧠 *Fetching AI Sentiment... Please wait...*",
    "ms": "🧠 *Sedang mengambil AI Sentiment... Sila tunggu...*",
    "id": "🧠 *Mengambil Sentimen AI... Mohon tunggu...*",
    "th": "🧠 *กำลังดึงข้อมูล AI Sentiment... กรุณารอสักครู่...*",
    "zh": "🧠 *正在获取 AI 情绪分析... 请稍等...*",
    "hi": "🧠 *AI भावना लोड हो रही है... कृपया प्रतीक्षा करें...*"
},
"sentiment_back_instruments": {
    "en": "🔁 Back to Instruments",
    "ms": "🔁 Kembali ke Instrumen",
    "id": "🔁 Kembali ke Instrumen",
    "th": "🔁 กลับไปยังสินทรัพย์",
    "zh": "🔁 返回选择品种",
    "hi": "🔁 इंस्ट्रूमेंट्स पर वापस जाएं"
},
"sentiment_back_menu": {
    "en": "🏠 Main Menu",
    "ms": "🏠 Menu Utama",
    "id": "🏠 Menu Utama",
    "th": "🏠 เมนูหลัก",
    "zh": "🏠 主菜单",
    "hi": "🏠 मुख्य मेनू"
},
"category_forex": {
  "en": "Forex", "ms": "Forex", "id": "Forex", "th": "ฟอเร็กซ์", "zh": "外汇", "hi": "फॉरेक्स"
},
"category_crypto": {
  "en": "Crypto", "ms": "Kripto", "id": "Kripto", "th": "คริปโต", "zh": "加密货币", "hi": "क्रिप्टो"
},
"category_index": {
  "en": "Index", "ms": "Indeks", "id": "Indeks", "th": "ดัชนี", "zh": "指数", "hi": "सूचकांक"
},
"category_metalsoil": {
  "en": "Metals & Oil", "ms": "Logam & Minyak", "id": "Logam & Minyak", "th": "โลหะและน้ำมัน", "zh": "金属与原油", "hi": "धातु और तेल"
},
"chart_back_timeframe": {
    "en": "🔁 Back to Timeframe",
    "ms": "🔁 Kembali ke Timeframe",
    "id": "🔁 Kembali ke Timeframe",
    "th": "🔁 กลับไปยัง Timeframe",
    "zh": "🔁 返回时间周期",
    "hi": "🔁 टाइमफ़्रेम पर वापस जाएं"
},
"chart_back_menu": {
    "en": "🏠 Main Menu",
    "ms": "🏠 Menu Utama",
    "id": "🏠 Menu Utama",
    "th": "🏠 เมนูหลัก",
    "zh": "🏠 主菜单",
    "hi": "🏠 मुख्य मेनू"
},
"technical_category_title": {
    "en": "📊 *Select a Market Category:*",
    "ms": "📊 *Pilih Kategori Pasaran:*",
    "id": "📊 *Pilih Kategori Pasar:*",
    "th": "📊 *เลือกหมวดหมู่ตลาด:*",
    "zh": "📊 *选择市场类别：*",
    "hi": "📊 *बाजार श्रेणी चुनें:*"
},
"technical_instrument_title": {
    "en": "📉 *Select an Instrument from {category}:*",
    "ms": "📉 *Pilih Instrumen dari {category}:*",
    "id": "📉 *Pilih Instrumen dari {category}:*",
    "th": "📉 *เลือกสินทรัพย์จาก {category}:*",
    "zh": "📉 *从 {category} 中选择品种：*",
    "hi": "📉 *{category} से इंस्ट्रूमेंट चुनें:*"
},
"technical_timeframe_title": {
    "en": "🕒 *Select Timeframe for {symbol}:*",
    "ms": "🕒 *Pilih Timeframe untuk {symbol}:*",
    "id": "🕒 *Pilih Timeframe untuk {symbol}:*",
    "th": "🕒 *เลือกกรอบเวลา {symbol}:*",
    "zh": "🕒 *选择 {symbol} 的时间周期：*",
    "hi": "🕒 *{symbol} के लिए टाइमफ़्रेम चुनें:*"
},
"smart_signal_title": {
    "en": "*Select Your Elite AI Insights*",
    "ms": "*Pilih Isyarat AI Elit Anda*",
    "id": "*Pilih Wawasan AI Elit Anda*",
    "th": "*เลือกสัญญาณ AI อัจฉริยะของคุณ*",
    "zh": "*选择您的 AI 精准信号*",
    "hi": "*अपने एलीट AI सिग्नल चुनें*"
},
"btn_back": {
    "en": "🔙 Back",
    "ms": "🔙 Kembali",
    "id": "🔙 Kembali",
    "th": "🔙 ย้อนกลับ",
    "zh": "🔙 返回",
    "hi": "🔙 वापस"
},
"signal_error": {
    "en": "❌ Unable to fetch signal at this time. Please try again later.",
    "ms": "❌ Tidak dapat mengambil isyarat buat masa ini. Sila cuba lagi nanti.",
    "id": "❌ Tidak dapat mengambil sinyal saat ini. Silakan coba lagi nanti.",
    "th": "❌ ไม่สามารถดึงสัญญาณได้ในขณะนี้ โปรดลองอีกครั้งในภายหลัง",
    "zh": "❌ 当前无法获取信号，请稍后再试。",
    "hi": "❌ इस समय सिग्नल प्राप्त नहीं हो सका। कृपया बाद में पुनः प्रयास करें।"
},
"instrument_gold": {
    "en": "🏆 GOLD (XAUUSD)",
    "ms": "🏆 EMAS (XAUUSD)",
    "id": "🏆 EMAS (XAUUSD)",
    "th": "🏆 ทองคำ (XAUUSD)",
    "zh": "🏆 黄金 (XAUUSD)",
    "hi": "🏆 सोना (XAUUSD)"
},
"instrument_bitcoin": {
    "en": "₿ BITCOIN (BTC)",
    "ms": "₿ BITCOIN (BTC)",
    "id": "₿ BITCOIN (BTC)",
    "th": "₿ บิทคอยน์ (BTC)",
    "zh": "₿ 比特币 (BTC)",
    "hi": "₿ बिटकॉइन (BTC)"
},
"instrument_ethereum": {
    "en": "🔣 ETHEREUM (ETH)",
    "ms": "🔣 ETHEREUM (ETH)",
    "id": "🔣 ETHEREUM (ETH)",
    "th": "🔣 อีเธอเรียม (ETH)",
    "zh": "🔣 以太坊 (ETH)",
    "hi": "🔣 एथेरियम (ETH)"
},
"instrument_dowjones": {
    "en": "📈 DOW JONES (DJI)",
    "ms": "📈 DOW JONES (DJI)",
    "id": "📈 DOW JONES (DJI)",
    "th": "📈 ดาวโจนส์ (DJI)",
    "zh": "📈 道琼斯 (DJI)",
    "hi": "📈 डॉव जोन्स (DJI)"
},
"instrument_nasdaq": {
    "en": "📊 NASDAQ (IXIC)",
    "ms": "📊 NASDAQ (IXIC)",
    "id": "📊 NASDAQ (IXIC)",
    "th": "📊 แนสแด็ก (IXIC)",
    "zh": "📊 纳斯达克 (IXIC)",
    "hi": "📊 नैस्डैक (IXIC)"
},
"instrument_eurusd": {
    "en": "💶 EUR/USD (EURUSD)",
    "ms": "💶 EUR/USD (EURUSD)",
    "id": "💶 EUR/USD (EURUSD)",
    "th": "💶 ยูโร/ดอลลาร์ (EURUSD)",
    "zh": "💶 欧元/美元 (EURUSD)",
    "hi": "💶 यूरो/यूएसडी (EURUSD)"
},
"instrument_gbpusd": {
    "en": "💷 GBP/USD (GBPUSD)",
    "ms": "💷 GBP/USD (GBPUSD)",
    "id": "💷 GBP/USD (GBPUSD)",
    "th": "💷 ปอนด์/ดอลลาร์ (GBPUSD)",
    "zh": "💷 英镑/美元 (GBPUSD)",
    "hi": "💷 जीबीपी/यूएसडी (GBPUSD)"
},
"timeframe_labels": {
    "en": {
        "1m": "1 Minute",
        "5m": "5 Minutes",
        "15m": "15 Minutes",
        "30m": "30 Minutes",
        "1h": "1 Hour",
        "4h": "4 Hours",
        "1D": "1 Day",
        "1W": "1 Week",
        "1M": "1 Month"
    },
    "ms": {
        "1m": "1 Minit",
        "5m": "5 Minit",
        "15m": "15 Minit",
        "30m": "30 Minit",
        "1h": "1 Jam",
        "4h": "4 Jam",
        "1D": "1 Hari",
        "1W": "1 Minggu",
        "1M": "1 Bulan"
    },
    "id": {
        "1m": "1 Menit",
        "5m": "5 Menit",
        "15m": "15 Menit",
        "30m": "30 Menit",
        "1h": "1 Jam",
        "4h": "4 Jam",
        "1D": "1 Hari",
        "1W": "1 Minggu",
        "1M": "1 Bulan"
    },
    "th": {
        "1m": "1 นาที",
        "5m": "5 นาที",
        "15m": "15 นาที",
        "30m": "30 นาที",
        "1h": "1 ชั่วโมง",
        "4h": "4 ชั่วโมง",
        "1D": "1 วัน",
        "1W": "1 สัปดาห์",
        "1M": "1 เดือน"
    },
    "zh": {
        "1m": "1 分钟",
        "5m": "5 分钟",
        "15m": "15 分钟",
        "30m": "30 分钟",
        "1h": "1 小时",
        "4h": "4 小时",
        "1D": "1 天",
        "1W": "1 周",
        "1M": "1 月"
    },
    "hi": {
        "1m": "1 मिनट",
        "5m": "5 मिनट",
        "15m": "15 मिनट",
        "30m": "30 मिनट",
        "1h": "1 घंटा",
        "4h": "4 घंटे",
        "1D": "1 दिन",
        "1W": "1 सप्ताह",
        "1M": "1 महीना"
    }
}



}

# Get translated text for current user
def get_text(user_id, key, context=None):
    """
    Fetches the translated string for the given user and key.
    It caches the language in context.user_data for performance.
    """
    # ✅ Check if cached
    if context and "user_lang" in context.user_data:
        lang = context.user_data["user_lang"]
    else:
        # ✅ If not cached, get from DB
        lang = get_user_language(user_id)

        # ✅ Store in cache for future use
        if context:
            context.user_data["user_lang"] = lang

    # ✅ Return translation or fallback
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("en", key))

