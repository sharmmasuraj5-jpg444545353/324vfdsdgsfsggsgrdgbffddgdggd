from pyrogram import Client, filters
from datetime import datetime
import pytz
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SONALI_MUSIC import app

def get_india_time():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    return now

@app.on_message(filters.command(["time", "date"]))
async def send_time_date(client, message):
    temp_msg = await message.reply_text("**⋟ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴜʀʀᴇɴᴛ ᴅᴀᴛᴇ & ᴛɪᴍᴇ...**")

    now = get_india_time()
    current_time = now.strftime("%H:%M:%S %p")
    current_date = now.strftime("%Y-%m-%d")
    day_name = now.strftime("%A")
    region = "Asia/Kolkata"

    response_text = (
        f"**⋟ ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇ & ᴅᴀᴛᴇ ɪɴ ɪɴᴅɪᴀ :-**\n\n"
        f"**➤ ᴛɪᴍᴇ :-** `{current_time}`\n"
        f"**➤ ᴅᴀᴛᴇ :-** `{current_date}`\n"
        f"**➤ ʀᴇɢɪᴏɴ :-** `{region}`\n"
        f"**➤ ᴅᴀʏ :-** `{day_name}`\n\n"
        f"**⋟ ʙʏ :- {app.mention}**"
    )

    await temp_msg.delete()

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
    )

    await message.reply_text(response_text, reply_markup=keyboard)
