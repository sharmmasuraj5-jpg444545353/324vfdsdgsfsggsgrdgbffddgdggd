import asyncio
import datetime
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from SONALI_MUSIC import app

INFO_TEXT = """
<u><b>👤 ᴜꜱᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>

<b>● ᴘʀᴏғɪʟᴇ ᴘɪᴄ ➠</b> [ᴄʟɪᴄᴋ ʜᴇʀᴇ]({})
<b>● ᴜꜱᴇʀ ɪᴅ ➠</b> <code>{}</code>
<b>● ᴜꜱᴇʀɴᴀᴍᴇ ➠</b> <code>@{}</code>
<b>● ᴍᴇɴᴛɪᴏɴ ➠</b> {}
<b>● ꜱᴛᴀᴛᴜꜱ ➠</b> {}
<b>● ᴅᴄ ɪᴅ ➠</b> {}
<b>● ᴄʀᴇᴀᴛᴇᴅ ᴏɴ ➠</b> {}
<b>● ᴘʀᴇᴍɪᴜᴍ ➠</b> {}
<b>● ꜱᴄᴀᴍ ➠</b> {}
<b>● ꜰᴀᴋᴇ ➠</b> {}
<b>● ꜱᴘᴀᴍ/ʀᴇꜱᴛʀɪᴄᴛ ➠</b> {}
<b>● ʟɪᴍɪᴛᴀᴛɪᴏɴ ➠</b> {}
<b>● ꜰʀᴏᴢᴇɴ ➠</b> {}
"""

def get_creation_date(user_id: int):
    """ Decode Telegram Snowflake ID into creation date """
    telegram_epoch = 1514764800000
    timestamp = (user_id >> 32) + telegram_epoch
    return datetime.datetime.utcfromtimestamp(timestamp / 1000)

async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "ʀᴇᴄᴇɴᴛʟʏ."
        elif x == enums.UserStatus.LAST_WEEK:
            return "ʟᴀꜱᴛ ᴡᴇᴇᴋ."
        elif x == enums.UserStatus.LONG_AGO:
            return "ꜱᴇᴇɴ ʟᴏɴɢ ᴀɢᴏ."
        elif x == enums.UserStatus.OFFLINE:
            return "ᴏꜰꜰʟɪɴᴇ."
        elif x == enums.UserStatus.ONLINE:
            return "ᴏɴʟɪɴᴇ."
    except:
        return "❌ ᴇʀʀᴏʀ"

@app.on_message(filters.command(["info", "information", "userinfo", "whois"], prefixes=["/", "!"]))
async def userinfo(_, message: Message):
    chat_id = message.chat.id

    try:
        user_id = None

        # case: /info user_id | username
        if not message.reply_to_message and len(message.command) == 2:
            user_id = message.text.split(None, 1)[1]

        # case: reply to someone
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id

        # case: no input
        else:
            await message.reply_text("**⚠️ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴜꜱᴇʀɴᴀᴍᴇ, ɪᴅ ᴏʀ ʀᴇᴘʟʏ ᴀꜰᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**")
            return

        # get user info
        user_info = await app.get_chat(user_id)   
        user = await app.get_users(user_id)       
        status = await userstatus(user.id)

        creation_date = get_creation_date(user.id).strftime("%d-%m-%Y %H:%M:%S")

        scam = "⚠️ ʏᴇꜱ" if user.is_scam else "✅ ɴᴏ"
        fake = "⚠️ ʏᴇꜱ" if user.is_fake else "✅ ɴᴏ"
        premium = "✅ ʏᴇꜱ" if user.is_premium else "❌ ɴᴏ"
        frozen = "❄️ ʏᴇꜱ" if getattr(user_info, "is_frozen", False) else "✅ ɴᴏ"

        # restriction/ban check
        if user_info.is_restricted:
            restriction_reason = user_info.restriction_reason[0].reason if user_info.restriction_reason else "ᴜɴᴋɴᴏᴡɴ"
            limitation = f"⛔ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ({restriction_reason})"
        elif user_info.is_deleted:
            limitation = "☠️ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ"
        else:
            limitation = "✅ ɴᴏ ʟɪᴍɪᴛᴀᴛɪᴏɴꜱ"

        # profile link
        if user.username:
            profile_url = f"https://t.me/{user.username}"
        else:
            profile_url = f"tg://user?id={user.id}"

        # profile photo link
        photos = await app.get_profile_photos(user.id, limit=1)
        if photos:
            sent = await app.send_photo(chat_id, photos[0].file_id, caption=".")
            photo_link = f"https://t.me/c/{str(chat_id)[4:]}/{sent.id}"
            await sent.delete()
        else:
            photo_link = profile_url

        # send final info
        await app.send_message(
            chat_id,
            text=INFO_TEXT.format(
                photo_link,
                user.id,
                user.username or "N/A",
                user.mention,
                status,
                user.dc_id,
                creation_date,
                premium,
                scam,
                fake,
                "⚠️ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ" if user_info.is_restricted else "✅ ɴᴏ",
                limitation,
                frozen
            ),
            reply_to_message_id=message.id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"{user.first_name}", url=profile_url),
                        InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            ),
            disable_web_page_preview=True
        )

    except Exception as e:
        await message.reply_text(str(e))
