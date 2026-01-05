from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app
from Dev import db

verified_col = db.verified_users


# ─────────────────────────────
# CHECK VERIFIED
# ─────────────────────────────
async def is_verified(user_id: int) -> bool:
    return bool(verified_col.find_one({"user_id": user_id}))


# ─────────────────────────────
# SAVE VERIFIED
# ─────────────────────────────
async def save_verified(user_id: int):
    verified_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )


# ─────────────────────────────
# VERIFY VIA START PARAM
# /start verify OR ?start=verify
# ─────────────────────────────
@app.on_message(filters.private & filters.command("start"))
async def verify_user(client, message):
    if len(message.command) < 2:
        return

    if message.command[1].lower() != "verify":
        return

    await save_verified(message.from_user.id)

    await message.reply_text(
        "✅ **Human Verification Successful**\n\n"
        "Ab aap group me freely message bhej sakte ho."
    )


# ─────────────────────────────
# GROUP MESSAGE GUARD
# ─────────────────────────────
@app.on_message(filters.group & ~filters.service & ~filters.me)
async def verify_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
        return

    # Admin skip
    try:
        m = await client.get_chat_member(chat.id, user.id)
        if m.status in ("administrator", "owner"):
            return
    except:
        return

    # Already verified → allow
    if await is_verified(user.id):
        return

    # ❌ Not verified → delete msg
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
            "❌ Without Verification Msg Bot Allowed.\n"
            "👇 Continue karne ke liye verify kre",
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
