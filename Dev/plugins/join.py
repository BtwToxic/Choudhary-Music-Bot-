from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app, db


@app.on_message(filters.group & ~filters.service & ~filters.me)
async def verify_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
        return

    # Admin / owner skip
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "owner"):
            return
    except:
        return

    # Already verified
    if await db.is_verified(user.id):
        return

    # Delete message
    try:
        await message.delete()
    except:
        pass

    # Warning + start=verify button
    try:
        bot = await client.get_me()
        await client.send_message(
            chat.id,
            f"⚠️ **Human Verification Required**\n\n"
            f"👤 {user.mention}\n\n"
            "You must verify before sending messages in this group.\n"
            "Click the button below to verify:",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "🤖 Start Verification",
                        url=f"https://t.me/{bot.username}?start=verify"
                    )
                ]]
            )
        )
    except:
        pass
