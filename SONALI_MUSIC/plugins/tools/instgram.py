import re
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from SONALI_MUSIC import app
from config import LOGGER_ID


@app.on_message(filters.command(["ig", "instagram", "reel"]))
async def download_instagram_video(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "**ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ 🙌**"
        )
        return

    url = message.text.split()[1]
    if not re.match(
        re.compile(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"), url
    ):
        return await message.reply_text(
            "**ᴛʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ ᴜʀʟ ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ɪɴsᴛᴀɢʀᴀᴍ ᴜʀʟ 😅😅**"
        )

    a = await message.reply_text("**🎀 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...**")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    response = requests.get(api_url)
    try:
        result = response.json()
        data = result["result"]
    except Exception as e:
        f = f"ᴇʀʀᴏʀ :\n{e}"
        try:
            await a.edit(f)
        except Exception:
            await message.reply_text(f)
            return await app.send_message(LOGGER_ID, f)
        return await app.send_message(LOGGER_ID, f)

    if not result["error"]:
        video_url = data["url"]
        duration = data["duration"]
        quality = data["quality"]
        type = data["extension"]
        size = data["formattedSize"]
        caption = f"**◍ ᴅᴜʀᴀᴛɪᴏɴ :** {duration}\n**◍ ǫᴜᴀʟɪᴛʏ :** {quality}\n**◍ ᴛʏᴘᴇ :** {type}\n**◍ sɪᴢᴇ :** {size}"
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url="https://t.me/Sonali_Music_bot?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")]
            ]
        )
        await a.delete()
        await message.reply_video(video_url, caption=caption, reply_markup=buttons)
    else:
        try:
            return await a.edit("ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")
        except Exception:
            return await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")
