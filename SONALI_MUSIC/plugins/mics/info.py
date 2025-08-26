import datetime
import aiohttp
import os
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
"""

# --- account creation date (approx) ---
def get_creation_date(user_id: int):
    try:
        timestamp = (user_id >> 32) + 1390000000
        return datetime.datetime.utcfromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")
    except:
        return "Unknown"

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
        return "❌ ᴇʀʀᴏʀ"

# --- upload file to catbox ---
async def upload_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, files={"fileToUpload": open(file_path, "rb")}) as resp:
            return await resp.text()

# --- main command handler ---
@app.on_message(filters.command(["info", "information", "userinfo", "whois"], prefixes=["/", "!"]))
async def userinfo(_, message: Message):
    try:
        user_id = None

        # case: /info user_id | username
        if not message.reply_to_message and len(message.command) == 2:
            user_id = message.text.split(None, 1)[1]

        # case: reply to someone
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id

        # case: no input - show own info
        else:
            user_id = message.from_user.id

        # get user info
        user = await app.get_users(user_id)
        status = await userstatus(user.id)
        creation_date = get_creation_date(user.id)

        scam = "ʏᴇꜱ" if user.is_scam else "ɴᴏ"
        premium = "ʏᴇꜱ" if user.is_premium else "ɴᴏ"

        # default profile link
        profile_url = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
        photo_link = profile_url

        # try to get profile photo & upload to catbox
        try:
            photos = await app.get_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                file_path = await app.download_media(photos.photos[0].file_id, file_name=f"{user.id}.jpg")
                photo_link = await upload_catbox(file_path)
                os.remove(file_path)  # cleanup
        except Exception as e:
            print(f"Error getting profile photo: {e}")

        # send info
        await message.reply_text(
            text=INFO_TEXT.format(
                photo_link,
                user.id,
                user.username or "N/A",
                user.mention,
                status,
                user.dc_id or "N/A",
                creation_date,
                premium,
                scam,
            ),
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(f"{user.first_name}", callback_data=f"userinfo_{user.id}"),
                    InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")
                ]]
            ),
            disable_web_page_preview=True,
        )

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
