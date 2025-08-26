import asyncio
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from SONALI_MUSIC import app

INFO_TEXT = """
<u><b>👤 ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>

<b>● ᴘʀᴏғɪʟᴇ ᴘɪᴄ ➠</b> [ᴄʟɪᴄᴋ ʜᴇʀᴇ]({})

<b>● ᴜsᴇʀ ɪᴅ ➠</b> <code>{}</code>
<b>● ᴜsᴇʀɴᴀᴍᴇ ➠</b> <code>@{}</code>
<b>● ᴍᴇɴᴛɪᴏɴ ➠</b> {}
<b>● ᴜsᴇʀ sᴛᴀᴛᴜs ➠</b> {}
<b>● ᴜsᴇʀ ᴅᴄ ɪᴅ ➠</b> {}
"""

async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "recently."
        elif x == enums.UserStatus.LAST_WEEK:
            return "last week."
        elif x == enums.UserStatus.LONG_AGO:
            return "seen long ago."
        elif x == enums.UserStatus.OFFLINE:
            return "User is offline."
        elif x == enums.UserStatus.ONLINE:
            return "User is online."
    except:
        return "**✦ sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ʜᴀᴘᴘᴇɴᴇᴅ !**"

@app.on_message(filters.command(["info", "information", "userinfo", "whois"], prefixes=["/", "!"]))
async def userinfo(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        if not message.reply_to_message and len(message.command) == 2:
            user_id = message.text.split(None, 1)[1]
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id

        user_info = await app.get_chat(user_id)
        user = await app.get_users(user_id)
        status = await userstatus(user.id)

        id = user_info.id
        dc_id = user.dc_id
        username = user_info.username or "N/A"
        mention = user.mention

        if user.username:
            profile_url = f"https://t.me/{user.username}"
        else:
            profile_url = f"tg://user?id={user.id}"

        # Get profile photo link
        photos = await app.get_profile_photos(user.id, limit=1)
        if photos:
            # upload photo in current chat invisibly
            sent = await app.send_photo(chat_id, photos[0].file_id, caption=".")
            photo_link = sent.photo.file_id  
            photo_link = f"https://t.me/c/{str(chat_id)[4:]}/{sent.id}"
            await sent.delete() 
        else:
            photo_link = profile_url

        await app.send_message(
            chat_id,
            text=INFO_TEXT.format(photo_link, id, username, mention, status, dc_id),
            reply_to_message_id=message.id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"{user.first_name}", url=profile_url),
                        InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")
                    ]
                ]
            ),
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(str(e))
