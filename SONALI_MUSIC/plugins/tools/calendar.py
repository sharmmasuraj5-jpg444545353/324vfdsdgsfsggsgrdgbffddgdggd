from pyrogram import Client, filters
from PIL import Image, ImageEnhance
from io import BytesIO
import aiohttp
import calendar
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SONALI_MUSIC import app

async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"code": code}) as resp:
            image_data = await resp.read()

    carbon_image = Image.open(BytesIO(image_data))

    enhancer = ImageEnhance.Brightness(carbon_image)
    bright_image = enhancer.enhance(1.7)

    output_image = BytesIO()
    bright_image.save(output_image, format='PNG', quality=95)
    output_image.name = "carbon.png"
    return output_image


@app.on_message(filters.command("calendar", prefixes="/"))
async def send_calendar(_, message):
    command_parts = message.text.split(" ")
    if len(command_parts) == 2:
        try:
            year = int(command_parts[1])
        except ValueError:
            await message.reply("**ɪɴᴠᴀʟɪᴅ ʏᴇᴀʀ ꜰᴏʀᴍᴀᴛ.**\n\n**ᴜꜱᴇ** `/calendar <year>`")
            return
    else:
        await message.reply("**⋟ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ʏᴇᴀʀ ᴀꜰᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**\n\n**⋟ ᴜsᴀɢᴇ :-** `/calender 2025`")
        return

    cal = calendar.TextCalendar()
    full_year_calendar = cal.formatyear(year, 2, 1, 1, 3)

    carbon_image = await make_carbon(full_year_calendar)

    caption = f"**⋟ ᴄᴀʟᴇɴᴅᴀʀ ᴏғ ʏᴇᴀʀ :-** `{year}`\n\n**⋟ ʙʏ :-** <u>{app.mention}</u>"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
    )

    await app.send_photo(
        message.chat.id,
        carbon_image,
        caption=caption,
        reply_markup=keyboard
    )
