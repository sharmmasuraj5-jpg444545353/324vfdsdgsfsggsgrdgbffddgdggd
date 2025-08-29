import os
import random
import requests
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputVideoStream
import yt_dlp
from SONALI_MUSIC import app
# -------------------- VIDEO CACHE --------------------
vdo_link = {}  # chat_id: video_path

# -------------------- PYTG CALLS INIT --------------------
# aapke main bot module me app pass karenge
def init_pytgcalls(app):
    pytgcalls = PyTgCalls(app)
    return pytgcalls

# -------------------- UTILITY FUNCTIONS --------------------
async def get_video_stream(link: str) -> str:
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
    }
    x = yt_dlp.YoutubeDL(ydl_opts)
    info = x.extract_info(link, False)
    video = os.path.join("downloads", f"{info['id']}.{info['ext']}")
    if os.path.exists(video):
        return video
    x.download([link])
    return video


def get_video_info(title: str):
    url_base = f'https://www.xnxx.com/search/{title}'
    try:
        with requests.Session() as s:
            r = s.get(url_base)
            soup = BeautifulSoup(r.text, "html.parser")
            video_list = soup.findAll('div', attrs={'class': 'thumb-block'})
            if video_list:
                random_video = random.choice(video_list)
                thumbnail = random_video.find('div', class_="thumb").find('img').get("src")
                if thumbnail:
                    thumbnail_500 = thumbnail.replace('/h', '/m').replace('/1.jpg', '/3.jpg')
                link = random_video.find('div', class_="thumb-under").find('a').get("href")
                if link and 'https://' not in link:
                    return {'link': 'https://www.xnxx.com' + link, 'thumbnail': thumbnail_500}
    except Exception as e:
        print(f"Error: {e}")
        return None

# -------------------- VC PLAY FUNCTION --------------------
async def play(pytgcalls, chat_id: int, video_path: str):
    """
    Play video in VC using PyTgCalls
    """
    try:
        await pytgcalls.join_group_call(
            chat_id,
            InputVideoStream(video_path)
        )
    except Exception as e:
        print(f"❌ Error while joining VC: {e}")


# -------------------- COMMAND HANDLERS --------------------
def register_commands(app, pytgcalls):
    @app.on_message(filters.command(["porn", "xnxx"]))
    async def get_random_video_info(client, message: Message):
        if len(message.command) == 1:
            return await message.reply("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴛɪᴛʟᴇ ᴛᴏ sᴇᴀʀᴄʜ.")

        title = " ".join(message.command[1:])
        video_data = get_video_info(title)
        if not video_data:
            return await message.reply("❌ ɴᴏ ᴠɪᴅᴇᴏ ғᴏᴜɴᴅ")

        video_path = await get_video_stream(video_data['link'])
        vdo_link[message.chat.id] = video_path  # cache for callback

        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("▶️ ᴘʟᴀʏ ɪɴ ᴠᴄ", callback_data=f"vplay_{message.chat.id}")],
                [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close_data")]
            ]
        )

        await message.reply_photo(
            photo=video_data['thumbnail'],
            caption=f"🎬 ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ: {title}",
            reply_markup=buttons
        )

# -------------------- CALLBACKS --------------------
def register_callbacks(app, pytgcalls):
    @app.on_callback_query(filters.regex("^vplay"))
    async def vplay_callback(_, query: CallbackQuery):
        try:
            data = query.data.split("_")
            if len(data) > 1 and data[1].isdigit():
                chat_id = int(data[1])
            else:
                return await query.answer("❌ Invalid callback", show_alert=True)

            video_path = vdo_link.get(chat_id)
            if not video_path:
                return await query.answer("❌ No video chosen", show_alert=True)

            await play(pytgcalls, chat_id, video_path)
            await query.answer("▶️ Playing in VC")
        except Exception as e:
            await query.answer(f"❌ Error: {e}", show_alert=True)
            print(e)

    @app.on_callback_query(filters.regex("^close_data"))
    async def close_callback(_, query: CallbackQuery):
        try:
            await query.message.delete()
            await query.answer("❌ ᴄʟᴏsᴇᴅ")
        except Exception as e:
            await query.answer(f"❌ Error: {e}", show_alert=True)
            print(e)
