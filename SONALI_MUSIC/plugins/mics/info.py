import os
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from SONALI_MUSIC import app


INFO_TEXT = """
<u><b>👤 ᴜꜱᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>

<b>● ғɪʀsᴛ ɴᴀᴍᴇ ➠</b> {first}
<b>● ʟᴀsᴛ ɴᴀᴍᴇ ➠</b> {last}
<b>● ᴜꜱᴇʀ ɪᴅ ➠</b> <code>{id}</code>
<b>● ᴜꜱᴇʀɴᴀᴍᴇ ➠</b> @{username}
<b>● ᴍᴇɴᴛɪᴏɴ ➠</b> {mention}
<b>● ꜱᴛᴀᴛᴜꜱ ➠</b> {status}
<b>● ᴅᴄ ɪᴅ ➠</b> {dcid}
<b>● ᴘʀᴇᴍɪᴜᴍ ➠</b> {premium}
<b>● ꜱᴄᴀᴍ ➠</b> {scam}

<b>● ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➠ <a href="https://t.me/purvi_bots">ᴘᴜʀᴠɪ-ʙᴏᴛꜱ</a></b>
"""


# --- user online status ---
async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "ʀᴇᴄᴇɴᴛʟʏ"
        elif x == enums.UserStatus.LAST_WEEK:
            return "ʟᴀꜱᴛ ᴡᴇᴇᴋ"
        elif x == enums.UserStatus.LONG_AGO:
            return "ʟᴏɴɢ ᴀɢᴏ"
        elif x == enums.UserStatus.OFFLINE:
            return "ᴏꜰꜰʟɪɴᴇ"
        elif x == enums.UserStatus.ONLINE:
            return "ᴏɴʟɪɴᴇ"
    except:
        return "ᴇʀʀᴏʀ"


# --- main command handler ---
@app.on_message(filters.command(["info", "information", "userinfo", "whois"], prefixes=["/", "!"]))
async def userinfo(_, message: Message):
    try:
        # user target detect
        if not message.reply_to_message and len(message.command) == 2:
            user_id = message.text.split(None, 1)[1]
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        elif not message.reply_to_message and len(message.command) == 1:
            return await message.reply_text("**✦ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴜꜱᴇʀɴᴀᴍᴇ, ɪᴅ ᴏʀ ʀᴇᴘʟʏ ᴀꜰᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**")
        else:
            user_id = message.from_user.id

        # get user
        user = await app.get_users(user_id)
        status = await userstatus(user.id)

        scam = "ʏᴇꜱ" if user.is_scam else "ɴᴏ"
        premium = "ʏᴇꜱ" if user.is_premium else "ɴᴏ"

        profile_url = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"

        # send info
        await message.reply_text(
            text=INFO_TEXT.format(
                first=user.first_name or "N/A",
                last=user.last_name or "N/A",
                id=user.id,
                username=user.username or "N/A",
                mention=user.mention,
                status=status,
                dcid=user.dc_id or "N/A",
                premium=premium,
                scam=scam,
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(f"{user.first_name}", url=profile_url)]]
            ),
            disable_web_page_preview=True,
        )

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
