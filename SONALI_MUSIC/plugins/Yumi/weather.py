from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SONALI_MUSIC import app


@app.on_message(filters.command("weather"))
async def weather(client, message):
    try:
        user_input = message.command[1]
        location = user_input.strip()
        weather_url = f"https://wttr.in/{location}.png"
        
        caption = (
            "**⋟ ʜᴇʀᴇ's ᴡᴇᴀᴛʜᴇʀ ᴏғ ʏᴏᴜʀ ʟᴏᴄᴀᴛɪᴏɴ**\n"
            f"**⊙ ᴄʜᴇᴄᴋ ʙʏ :- {app.mention}**"
        )
      
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]
            ]
        )
        
        await message.reply_photo(photo=weather_url, caption=caption, reply_markup=keyboard)
    except IndexError:
        await message.reply_text("**⋟ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ʟᴏᴄᴀᴛɪᴏɴ.**\n\n**➻ ᴜsᴀɢᴇ :-** `/weather india`")
