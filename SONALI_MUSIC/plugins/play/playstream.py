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



# ================ GROUP + PRIVATE CMDS ==================
@app.on_message(filters.command("playstream"))
async def play_stream(client, message):
    chat = message.chat
    user_id = message.from_user.id

    if chat.type == ChatType.PRIVATE:
        user_groups = rtmp_col.find_one({"user_id": user_id})
        if not user_groups:
            return await message.reply(
                "**⚠️ ᴘʟᴇᴀsᴇ sᴇᴛ ʀᴛᴍᴘ ғɪʀsᴛ ᴜsɪɴɢ /setrtmp group_id rtmp_link**"
            )
        else:
            return await message.reply(
                "**✅ ɴᴏᴡ ᴜsᴇ :-** `/playstream song name` **ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.**"
            )

    elif chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        group_id = chat.id
        user_rtmp = get_rtmp(group_id)

        if not user_rtmp:
            return await message.reply(
                "**⚠️ ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ɴᴏ ʀᴛᴍᴘ sᴇᴛ.**\n\n**👉 sᴇᴛ ɪᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴜsɪɴɢ** `/setrtmp`"
            )

        if len(message.command) < 2:
            return await message.reply("**❌ ᴜsᴀɢᴇ :-** `/playstream song name`")

        await message.delete()
        query = " ".join(message.command[1:])
        user_mention = message.from_user.mention if message.from_user else "Unknown User"
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
        if not video_url:
            return await message.reply(f"**❌ ɴᴏ ʀᴇsᴜʟᴛ ғᴏᴜɴᴅ ғᴏʀ :-** {query}")

        title = data.get("title", "Unknown Title")
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

            msg = (
                f"**📡 sᴛʀᴇᴀᴍɪɴɢ ɴᴏᴡ...**\n\n"
                f"**🎵 ᴛɪᴛʟᴇ :-** {title}\n\n"
                f"**🙋 ᴘʟᴀʏᴇᴅ ʙʏ :-** {user_mention}"
            )

            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
                    url=f"https://t.me/{app.username}?startgroup=true"
                )]
            ])

            await message.reply(msg, reply_markup=buttons)

        except Exception as e:
            await message.reply(f"**❌ ғғᴍᴘᴇɢ ғᴀɪʟᴇᴅ :-** {e}")

# ================= END STREAM ==================
@app.on_message(filters.command("endstream"))
async def end_stream(client, message):
    user_id = message.from_user.id
    chat = message.chat

    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        try:
            member = await client.get_chat_member(chat.id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply("**⚠️ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴛᴏᴘ ᴛʜᴇ sᴛʀᴇᴀᴍ !!**")
        except Exception as e:
            return await message.reply(f"**❌ ᴇʀʀᴏʀ :-** {e}")

    kill_ffmpeg(chat.id)
    tmp_path = TMP_FILE.format(chat_id=chat.id)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    await message.reply(f"**🛑 sᴛʀᴇᴀᴍ sᴛᴏᴘᴘᴇᴅ ʙʏ :-** {message.from_user.mention}")
