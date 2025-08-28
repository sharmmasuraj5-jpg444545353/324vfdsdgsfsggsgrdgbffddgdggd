from pyrogram import Client, filters
from datetime import datetime
import pytz
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SONALI_MUSIC import app


def get_current_time():
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)
    return current_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")


@app.on_message(filters.command(["time"]))
async def send_time(client, message):
    temp_msg = await message.reply_text("**⋟ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇ...**")

    time = get_current_time()
    response_text = f"**⋟ ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇ ɪɴ ɪɴᴅɪᴀ :-**\n\n`{time}`"

    await temp_msg.delete()

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
    )

    await message.reply_text(response_text, reply_markup=keyboard)
