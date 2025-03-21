# utils.py
async def safe_replace_message(query, context, text, reply_markup=None, parse_mode="Markdown"):
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception:
        try:
            await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
