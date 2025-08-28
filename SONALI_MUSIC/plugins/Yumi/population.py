from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from SONALI_MUSIC import app


def code_to_flag(country_code: str) -> str:
    return "".join([chr(127397 + ord(c)) for c in country_code.upper()])


@app.on_message(filters.command("population"))
async def country_command_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "**⋟ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ.**\n\n**⋟ ᴜsᴀɢᴇ :-** `/population IN`"
        )
        return

    country_code = message.text.split(maxsplit=1)[1].strip()
    temp_msg = await message.reply_text(
        f"**⋟ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴅᴀᴛᴀ ꜰᴏʀ :-** `{country_code}`"
    )

    api_url = f"https://restcountries.com/v3.1/alpha/{country_code}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        country_info = response.json()
        if country_info:
            info = country_info[0]

            country_name = info.get("name", {}).get("common", "N/A")
            capital = info.get("capital", ["N/A"])[0]
            population = f"{info.get('population', 'N/A'):,}"
            region = info.get("region", "N/A")
            subregion = info.get("subregion", "N/A")
            area = f"{info.get('area', 'N/A'):,} km²"
            timezone = ", ".join(info.get("timezones", ["N/A"]))
            languages = ", ".join(info.get("languages", {}).values()) if "languages" in info else "N/A"
            calling_codes = ", ".join(info.get("idd", {}).get("root", "") + x for x in info.get("idd", {}).get("suffixes", [])) if "idd" in info else "N/A"

            flag = code_to_flag(country_code)

            response_text = (
                f"**⋟ ᴄᴏᴜɴᴛʀʏ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ :-** {flag}\n\n"
                f"**➤ ɴᴀᴍᴇ :-** `{country_name}`\n"
                f"**➤ ᴄᴀᴘɪᴛᴀʟ :-** `{capital}`\n"
                f"**➤ ᴘᴏᴘᴜʟᴀᴛɪᴏɴ :-** `{population}`\n"
                f"**➤ ʀᴇɢɪᴏɴ :-** `{region}`\n"
                f"**➤ sᴜʙʀᴇɢɪᴏɴ :-** `{subregion}`\n"
                f"**➤ ᴀʀᴇᴀ :-** `{area}`\n"
                f"**➤ ᴛɪᴍᴇᴢᴏɴᴇ :-** `{timezone}`\n"
                f"**➤ ʟᴀɴɢᴜᴀɢᴇs :-** `{languages}`\n"
                f"**➤ ᴄᴀʟʟɪɴɢ ᴄᴏᴅᴇ :-** `{calling_codes}`\n\n"
                f"**⋟ ʙʏ :- {app.mention}**"
            )
        else:
            response_text = "⚠️ **ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴄᴏᴜɴᴛʀʏ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ꜰʀᴏᴍ ᴛʜᴇ ᴀᴘɪ.**"
    except requests.exceptions.HTTPError:
        response_text = "⚠️ **ʜᴛᴛᴘ ᴇʀʀᴏʀ. ᴇɴᴛᴇʀ ᴄᴏʀʀᴇᴄᴛ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ.**"
    except Exception:
        response_text = "⚠️ **ᴇʀʀᴏʀ ᴡʜɪʟᴇ ꜰᴇᴛᴄʜɪɴɢ ᴅᴀᴛᴀ.**"

    await temp_msg.delete()
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
    )
    await message.reply_text(response_text, reply_markup=keyboard)
