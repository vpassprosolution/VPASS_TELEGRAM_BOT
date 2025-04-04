import psycopg2
import asyncio
import ai_signal_handler
from channel_verification import check_membership
from telegram.ext import JobQueue

from db import connect_db
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from ai_technical_handler import (
    show_categories,
    show_technical_instruments,
    show_timeframes,
    fetch_chart,
)

from utils import safe_replace_message

from language_handler import get_text, show_language_menu, set_language
from live_chat_handler import (
    handle_live_chat_entry,
    handle_user_message,
    active_live_chat_users,
    route_text_message,
    exit_live_chat  # ✅ Add this
)

from social_media import social_media
from auto_copy_handler import (
    auto_copy_menu,
    subscribe_copy,
    unsubscribe_copy
)


from subscription_handler import show_instruments as show_smart_signal_instruments, show_subscription_menu, subscribe, unsubscribe, back_to_main, back_to_instruments

from menu import main_menu
from setup_handler import setup_menu, coming_soon
from registration_handler import (
    register_user,
    collect_user_data,
    confirm_phone_number,
    confirm_email,
    check_membership_callback
)
from start_handler import start, start_vpass_pro


# Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"

# Step tracking for user registration
user_steps = {}

# ✅ Step tracking for MT5 Auto Copy
user_mt5_steps = {}
user_risk_steps = {}



def main():
    """Main function to run the bot"""
    from channel_verification import verify_active_membership  

    app = Application.builder().token(BOT_TOKEN).build()
    job_queue = app.job_queue

    # ✅ Run membership verification every 30 minutes
    job_queue.run_repeating(verify_active_membership, interval=1800, first=10)  
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(register_user, pattern="register"))
    app.add_handler(CallbackQueryHandler(start_vpass_pro, pattern="start_vpass_pro"))  # ✅ FIXED
    app.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))
    
    app.add_handler(CallbackQueryHandler(ai_signal_handler.show_instruments, pattern="^ai_agent_signal$"))
    app.add_handler(CallbackQueryHandler(ai_signal_handler.fetch_ai_signal, pattern="^ai_signal_"))


    app.add_handler(CallbackQueryHandler(show_smart_signal_instruments, pattern="^vpass_smart_signal$"))
    app.add_handler(CallbackQueryHandler(show_subscription_menu, pattern="^select_"))
    app.add_handler(CallbackQueryHandler(subscribe, pattern="^subscribe_"))
    app.add_handler(CallbackQueryHandler(unsubscribe, pattern="^unsubscribe_"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    app.add_handler(CallbackQueryHandler(back_to_instruments, pattern="^back_to_instruments$"))
   
    
    app.add_handler(CallbackQueryHandler(confirm_phone_number, pattern="confirm_phone"))
    app.add_handler(CallbackQueryHandler(confirm_phone_number, pattern="reenter_phone"))
    app.add_handler(CallbackQueryHandler(confirm_email, pattern="confirm_email"))
    app.add_handler(CallbackQueryHandler(confirm_email, pattern="reenter_email"))
    app.add_handler(CallbackQueryHandler(check_membership_callback, pattern="check_membership"))  # ✅ Membership Verification

  
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^ai_technical$"))  # Entry button
    app.add_handler(CallbackQueryHandler(show_technical_instruments, pattern="^tech2_cat_"))
    app.add_handler(CallbackQueryHandler(show_timeframes, pattern="^tech2_symbol_"))
    app.add_handler(CallbackQueryHandler(fetch_chart, pattern="^tech2_chart_"))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^tech2_back_categories$"))
   
    
    app.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
    app.add_handler(CallbackQueryHandler(show_language_menu, pattern="^language_menu$"))
    app.add_handler(CallbackQueryHandler(setup_menu, pattern="^setup_menu$"))
    app.add_handler(CallbackQueryHandler(coming_soon, pattern="^coming_soon$"))
    
    app.add_handler(CallbackQueryHandler(handle_live_chat_entry, pattern="^live_chat$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text_message))
    app.add_handler(CallbackQueryHandler(exit_live_chat, pattern="^live_chat_exit$"))
    
    app.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))
    app.add_handler(CallbackQueryHandler(social_media, pattern="social_media"))
    

    app.add_handler(CallbackQueryHandler(auto_copy_menu, pattern="^auto_copy$"))
    app.add_handler(CallbackQueryHandler(subscribe_copy, pattern="^subscribe_copy$"))
    app.add_handler(CallbackQueryHandler(unsubscribe_copy, pattern="^unsubscribe_copy$"))




    print("Bot is running...")

    app.run_polling()

if __name__ == "__main__":
    main()
