from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app, mongodb


# ─────────────────────────────
# VERIFY VIA START PARAM ONLY
# /start verify OR ?start=verify
# ─────────────────────────────
@app.on_message(filters.private & filters.command("start"))
async def verify_user(client, message):
    # agar /start ke saath argument nahi hai → ignore
    if len(message.command) < 2:
        return

    # sirf verify ke liye
    if message.command[1].lower() != "verify":
        return

    await mongodb.add_verified(message.from_user.id)

    await message.reply_text(
        "✅ **Human Verification Successful**\n\n"
        "Ab aap group me freely message bhej sakte ho 🎉"
    )


# ─────────────────────────────
# GROUP VERIFICATION GUARD
# ─────────────────────────────
@app.on_message(filters.group & ~filters.service & ~filters.me)
async def verify_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
        return

    # Admin / Owner skip
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "owner"):
            return
    except:
        return

    # Agar already verified → allow
    if await mongodb.is_verified(user.id):
        return

    # ❌ Not verified → user ka msg delete
    try:
        await message.delete()
    except:
        pass

    # ⚠️ Warning with Start button
    try:
        bot = await client.get_me()
        await client.send_message(
            chat.id,
            f"⚠️ **Human Verification Required**\n\n"
            f"👤 {user.mention}\n\n"
            "❌ Bot start kiye bina message allowed nahi hai.\n"
            "👇 Verify karne ke liye bot start karein:",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "🤖 Start Bot",
                        url=f"https://t.me/{bot.username}?start=verify"
                    )
                ]]
            )
        )
    except:
        pass
