from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils import safe_replace_message
import psycopg2
import httpx

DATABASE_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"
BACKEND_URL = "https://vessa-mt5-backend-production.up.railway.app"

# ✅ Check if user is premium
def is_premium_user(user_id: int):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT is_premium FROM users WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result and result[0] == True
    except Exception as e:
        print("❌ Error checking premium:", e)
        return False

# ✅ Auto Copy Menu
async def auto_copy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_premium_user(user_id):
        await query.edit_message_text(
            "💎 This feature is only for *Premium Members*.\n\nPlease upgrade your account to access MT5 Auto Copy.",
            parse_mode="Markdown"
        )
        return

    keyboard = [
        [InlineKeyboardButton("📝 Fill My MT5 Details", url="https://vpassprosolution.github.io/vessa-mt5-miniapp/")],
        [InlineKeyboardButton("✅ Subscribe Copy", callback_data="subscribe_copy")],
        [InlineKeyboardButton("❌ Unsubscribe Copy", callback_data="unsubscribe_copy")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
    ]

    await safe_replace_message(
        query,
        context,
        text="🚀 *MT5 Auto Copy Menu*\n\nChoose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ✅ Subscribe user to MT5 Auto Copy
async def subscribe_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/set_copy_subscription", json={
                "user_id": user_id,
                "status": True
            })

        if response.status_code == 200:
            await query.edit_message_text("✅ You have successfully *subscribed* to MT5 Auto Copy!", parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ Failed to subscribe. Please try again.")
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {e}")

# ✅ Unsubscribe user from MT5 Auto Copy
async def unsubscribe_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/set_copy_subscription", json={
                "user_id": user_id,
                "status": False
            })

        if response.status_code == 200:
            await query.edit_message_text("❌ You have *unsubscribed* from MT5 Auto Copy.", parse_mode="Markdown")
        else:
            await query.edit_message_text("⚠️ Failed to unsubscribe. Please try again.")
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {e}")
