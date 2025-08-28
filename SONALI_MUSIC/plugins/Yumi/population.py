from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from SONALI_MUSIC import app


@app.on_message(filters.command("population"))
async def country_command_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("**⋟ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ.**\n\n**⋟ ᴜsᴀɢᴇ :-** `/population IN`")
        return

    country_code = message.text.split(maxsplit=1)[1].strip()
    temp_msg = await message.reply_text(f"**⋟ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴘᴏᴘᴜʟᴀᴛɪᴏɴ ᴅᴀᴛᴀ ꜰᴏʀ :-** `{country_code}`")

    api_url = f"https://restcountries.com/v3.1/alpha/{country_code}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        country_info = response.json()
        if country_info:
            country_name = country_info[0].get("name", {}).get("common", "N/A")
            capital = country_info[0].get("capital", ["N/A"])[0]
            population = country_info[0].get("population", "N/A")
            response_text = (
                f"**⋟ ᴄᴏᴜɴᴛʀʏ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ :-**\n\n"
                f"**➤ ɴᴀᴍᴇ :-** `{country_name}`\n"
                f"**➤ ᴄᴀᴘɪᴛᴀʟ :-** `{capital}`\n"
                f"**➤ ᴘᴏᴘᴜʟᴀᴛɪᴏɴ :-** `{population}`"
            )
        else:
            response_text = "⚠️ **ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴄᴏᴜɴᴛʀʏ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ꜰʀᴏᴍ ᴛʜᴇ ᴀᴘɪ.**"
    except requests.exceptions.HTTPError:
        response_text = "⚠️ **ʜᴛᴛᴘ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴇɴᴛᴇʀ ᴄᴏʀʀᴇᴄᴛ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ.**"
    except Exception:
        response_text = "⚠️ **ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ꜰᴇᴛᴄʜɪɴɢ ᴅᴀᴛᴀ.**"

    await temp_msg.delete()
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
    )
    await message.reply_text(response_text, reply_markup=keyboard)
