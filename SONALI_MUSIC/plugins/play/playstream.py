import os
import requests
import subprocess
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType, ChatMemberStatus
from pymongo import MongoClient
from config import MONGO_DB_URI as MONGO_URI
from SONALI_MUSIC import app

# ================== CONFIG ==================
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

def set_rtmp(user_id: int, group_id: int, link: str, group_name: str):
    rtmp_col.update_one(
        {"group_id": group_id},
        {"$set": {"user_id": user_id, "rtmp": link, "group_name": group_name}},
        upsert=True
    )

def clear_rtmp(group_id: int):
    rtmp_col.delete_one({"group_id": group_id})

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

def get_video_info(url_or_query: str):
    """Get video metadata using yt-dlp"""
    try:
        ydl_opts = {
            "quiet": True,
            "format": "best[ext=mp4]",
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # अगर query है तो ytsearch1:
            if "youtube.com" not in url_or_query and "youtu.be" not in url_or_query:
                info = ydl.extract_info(f"ytsearch1:{url_or_query}", download=False)
                if "entries" in info:
                    info = info["entries"][0]
            else:
                info = ydl.extract_info(url_or_query, download=False)

            return {
                "title": info.get("title", "Unknown Title"),
                "duration": info.get("duration_string", "N/A"),
                "uploader": info.get("uploader", "Unknown Channel"),
                "thumbnail": info.get("thumbnail"),
                "url": info.get("url")
            }
    except Exception as e:
        print(f"yt-dlp error: {e}")
        return None

# ================== PRIVATE CMDS ==================
@app.on_message(filters.command("setrtmp"))
async def set_rtmp_cmd(client, message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply("**⚠️ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ**")

    if len(message.command) < 3:
        return await message.reply("**❌ ᴜsᴀɢᴇ :-** /setrtmp group_id rtmp_link")

    try:
        group_id = int(message.command[1])
    except ValueError:
        return await message.reply("**⚠️ ɪɴᴠᴀʟɪᴅ ɢʀᴏᴜᴘ ɪᴅ**")

    link = message.command[2]
    if not link.startswith("rtmp"):
        return await message.reply("**⚠️ ɪɴᴠᴀʟɪᴅ ʀᴛᴍᴘ ʟɪɴᴋ.**")

    try:
        chat_info = await client.get_chat(group_id)
        group_name = chat_info.title
    except:
        group_name = "Unknown Group"

    kill_ffmpeg(group_id)
    set_rtmp(message.from_user.id, group_id, link, group_name)

    await message.reply(
        f"**✅ ʀᴛᴍᴘ ʟɪɴᴋ sᴇᴛ ғᴏʀ {group_name}** (`{group_id}`)\n\n**ʟɪɴᴋ :-** {link}"
    )

# ================ GROUP CMDS ==================
@app.on_message(filters.command("playstream"))
async def play_stream(client, message):
    chat = message.chat
    user_id = message.from_user.id

    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        group_id = chat.id
        user_rtmp = get_rtmp(group_id)

        if not user_rtmp:
            return await message.reply(
                "**⚠️ ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ɴᴏ ʀᴛᴍᴘ sᴇᴛ.**\n\n**👉 sᴇᴛ ɪᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴜsɪɴɢ** `/setrtmp`"
            )

        if len(message.command) < 2:
            return await message.reply("**❌ ᴜsᴀɢᴇ :-** `/playstream song name or youtube_link`")

        query = " ".join(message.command[1:])
        user_mention = message.from_user.mention if message.from_user else "Unknown User"
        searching_msg = await message.reply(f"**🔎 sᴇᴀʀᴄʜɪɴɢ :-** {query}")

        # -------- Get metadata --------
        info = get_video_info(query)
        if not info:
            return await searching_msg.edit("**❌ ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴅᴀᴛᴀ.**")

        video_url = info["url"]
        title = info["title"]
        duration = info["duration"]
        channel = info["uploader"]
        thumbnail = info["thumbnail"]

        # -------- Download video --------
        tmp_path = TMP_FILE.format(chat_id=group_id)
        try:
            with requests.get(video_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception as e:
            return await searching_msg.edit(f"**❌ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ :-** {e}")

        # -------- Start streaming --------
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

            caption = (
                f"**📡 Streaming Now...**\n\n"
                f"**🎵 Title :** {title}\n"
                f"**⏱ Duration :** {duration}\n"
                f"**📺 Channel :** {channel}\n\n"
                f"**🙋 Played by :** {user_mention}"
            )

            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="✙ Add Me To Your Group ✙",
                    url=f"https://t.me/{app.username}?startgroup=true"
                )]
            ])

            if thumbnail:
                await message.reply_photo(thumbnail, caption=caption, reply_markup=buttons)
            else:
                await message.reply(caption, reply_markup=buttons)

        except Exception as e:
            await message.reply(f"**❌ FFmpeg Failed :-** {e}")

# ================= END STREAM ==================
@app.on_message(filters.command("endstream"))
async def end_stream(client, message):
    user_id = message.from_user.id
    chat = message.chat

    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        try:
            member = await client.get_chat_member(chat.id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply("**⚠️ Only admins can stop the stream !!**")
        except Exception as e:
            return await message.reply(f"**❌ Error :-** {e}")

    kill_ffmpeg(chat.id)
    tmp_path = TMP_FILE.format(chat_id=chat.id)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    await message.reply(f"**🛑 Stream stopped by :-** {message.from_user.mention}")
