import os
import requests
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType, ChatMemberStatus
from pymongo import MongoClient
from config import MONGO_DB_URI as MONGO_URI
from SONALI_MUSIC import app

# ================== CONFIG ==================
API_URL   = "https://bitflow.in/api/youtube"
API_KEY   = "1spiderkey2"
TMP_FILE  = "/tmp/downloaded_video_{chat_id}.mp4"
PID_FILE  = "/tmp/ffmpeg_{chat_id}.pid"

# =============== MONGO DB CONFIG ===============
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["streambot"]
rtmp_col = db["group_rtmp"]

# ================ HELPERS ===================
def get_rtmp(group_id: int):
    data = rtmp_col.find_one({"group_id": group_id})
    return data.get("rtmp") if data else None

def kill_ffmpeg(chat_id: int):
    pid_path = PID_FILE.format(chat_id=chat_id)
    try:
        if os.path.exists(pid_path):
            with open(pid_path) as f:
                pid = int(f.read())
            os.kill(pid, 9)
            os.remove(pid_path)
        else:
            os.system("pkill -9 ffmpeg")
    except Exception as e:
        print(f"⚠️ KILL FFMPEG ERROR: {e}")


# ================ GROUP CMD ==================
@app.on_message(filters.command("playstream"))
async def play_stream(client, message):
    chat = message.chat

    if chat.type == ChatType.PRIVATE:
        return await message.reply("**⚠️ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ**")

    elif chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        group_id = chat.id
        user_rtmp = get_rtmp(group_id)

        if not user_rtmp:
            return await message.reply(
                "**⚠️ ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ɴᴏ ʀᴛᴍᴘ sᴇᴛ.**\n\n**👉 sᴇᴛ ɪᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴜsɪɴɢ** `/setrtmp`"
            )

        if len(message.command) < 2:
            return await message.reply("**❌ ᴜsᴀɢᴇ :-** `/playstream song name or link`")

        await message.delete()
        query = " ".join(message.command[1:])
        searching_msg = await message.reply(f"**🔎 sᴇᴀʀᴄʜɪɴɢ :-** {query}")

        try:
            response = requests.get(API_URL, params={
                "query": query,
                "format": "video",
                "api_key": API_KEY
            }, timeout=30)
            data = response.json()
        except Exception as e:
            return await message.reply(f"**❌ ᴀᴘɪ ᴇʀʀᴏʀ :-** {e}")

        video_url = data.get("url")
        title     = data.get("title", "Unknown Title")
        thumb     = data.get("thumbnail")

        if not video_url:
            return await message.reply(f"**❌ ɴᴏ ʀᴇsᴜʟᴛ ғᴏᴜɴᴅ ғᴏʀ :-** {query}")

        tmp_path = TMP_FILE.format(chat_id=group_id)

        try:
            with requests.get(video_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception as e:
            return await message.reply(f"**❌ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ :-** {e}")

        ffmpeg_command = [
            "ffmpeg", "-re", "-i", tmp_path,
            "-c:v", "copy", "-c:a", "aac",
            "-f", "flv", user_rtmp
        ]

        try:
            process = subprocess.Popen(ffmpeg_command)
            pid_path = PID_FILE.format(chat_id=group_id)
            with open(pid_path, "w") as f:
                f.write(str(process.pid))

            await searching_msg.delete()

            msg = f"**📡 sᴛʀᴇᴀᴍɪɴɢ ɴᴏᴡ...**\n\n**🎵 ᴛɪᴛʟᴇ :-** {title}"

            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
                    url=f"https://t.me/{app.username}?startgroup=true"
                )]
            ])

            # Thumbnail ke sath reply
            if thumb:
                await message.reply_photo(photo=thumb, caption=msg, reply_markup=buttons)
            else:
                await message.reply(msg, reply_markup=buttons)

        except Exception as e:
            await message.reply(f"**❌ ғғᴍᴘᴇɢ ғᴀɪʟᴇᴅ :-** {e}")
