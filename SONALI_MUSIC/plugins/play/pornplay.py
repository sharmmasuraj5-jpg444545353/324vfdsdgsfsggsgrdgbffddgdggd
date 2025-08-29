from pyrogram import filters
import requests, random, os, yt_dlp
from bs4 import BeautifulSoup
from SONALI_MUSIC import app
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from SONALI_MUSIC.plugins.play import play

# Cache
vdo_link = {}

# -------------------- CALLBACKS --------------------

@app.on_callback_query(filters.regex("^vplay"))
async def vplay_callback(_, query: CallbackQuery):
    try:
        data = query.data.split("_")
        if len(data) > 1 and data[1].isdigit():
            chat_id = int(data[1])
        else:
            return await query.answer("❌ ɪɴᴠᴀʟɪᴅ ᴄᴀʟʟʙᴀᴄᴋ", show_alert=True)

        await play(_, query.message)
        await query.answer("▶️ ᴠɪᴅᴇᴏ ᴘʟᴀʏʙᴀᴄᴋ sᴛᴀʀᴛᴇᴅ!")

    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


@app.on_callback_query(filters.regex("^close_data"))
async def close_callback(_, query: CallbackQuery):
    await query.message.delete()
    await query.answer("❌ ᴄʟᴏsᴇᴅ")


# -------------------- YTDLP VIDEO DOWNLOADER --------------------

async def get_video_stream(link):
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


# -------------------- VIDEO INFO SCRAPER --------------------

def get_video_info(title):
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


# -------------------- EXTRA INFO SCRAPER --------------------

def get_views_and_ratings(link):
    try:
        with requests.Session() as s:
            r = s.get(link)
            soup = BeautifulSoup(r.text, "html.parser")

            # Views text (example: "123,456 views")
            views = soup.find("span", class_="metadata")
            views = views.text.strip() if views else "N/A"

            # Rating percentage (example: "96%")
            rating = soup.find("span", class_="rating")
            rating = rating.text.strip() if rating else "N/A"

            return views, rating
    except Exception as e:
        print(f"Error scraping views/ratings: {e}")
        return "N/A", "N/A"


# -------------------- COMMAND HANDLERS --------------------

@app.on_message(filters.command("porn"))
async def get_random_video_info(client, message: Message):
    if len(message.command) == 1:
        return await message.reply("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴛɪᴛʟᴇ ᴛᴏ sᴇᴀʀᴄʜ.")

    title = ' '.join(message.command[1:])
    video_info = get_video_info(title)

    if video_info:
        video_link = video_info['link']
        video = await get_video_stream(video_link)

        vdo_link[message.chat.id] = {'link': video_link}

        keyboard1 = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊝ ᴄʟᴏsᴇ ⊝", callback_data="close_data"),
                InlineKeyboardButton("⊝ ᴠᴘʟᴀʏ ⊝", callback_data=f"vplay_{message.chat.id}"),
            ]
        ])
        await message.reply_video(
            video,
            caption=f"⧉ ᴛɪᴛʟᴇ: {title}",
            reply_markup=keyboard1
        )

    else:
        await message.reply(f"❌ ɴᴏ ᴠɪᴅᴇᴏ ʟɪɴᴋ ғᴏᴜɴᴅ ғᴏʀ '{title}'.")


@app.on_message(filters.command("xnxx"))
async def get_random_video_info_xnxx(client, message: Message):
    if len(message.command) == 1:
        return await message.reply("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴛɪᴛʟᴇ ᴛᴏ sᴇᴀʀᴄʜ.")

    title = ' '.join(message.command[1:])
    video_info = get_video_info(title)

    if video_info:
        video_link = video_info['link']
        video = await get_video_stream(video_link)

        views, ratings = get_views_and_ratings(video_link)

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⊝ ᴄʟᴏsᴇ ⊝", callback_data="close_data"),
                InlineKeyboardButton("⊝ ᴠᴘʟᴀʏ ⊝", callback_data=f"vplay_{message.chat.id}"),
            ]
        ])

        await message.reply_video(
            video,
            caption=f"⧉ ᴛɪᴛʟᴇ: {title}\n⧉ ᴠɪᴇᴡs: {views}\n⧉ ʀᴀᴛɪɴɢs: {ratings}",
            reply_markup=keyboard
        )
    else:
        await message.reply(f"❌ ɴᴏ ᴠɪᴅᴇᴏ ʟɪɴᴋ ғᴏᴜɴᴅ ғᴏʀ '{title}'.")
