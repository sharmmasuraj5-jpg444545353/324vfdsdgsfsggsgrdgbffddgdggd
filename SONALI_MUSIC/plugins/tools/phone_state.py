from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json
import pycountry
from SONALI_MUSIC import app

async def send_message(message, text, reply_markup=None):
    await message.reply_text(text, reply_markup=reply_markup)


@app.on_message(filters.command("getstate"))
async def get_states(client, message):
    try:
        if len(message.text.split()) < 2:
            usage_text = (
                "**⋟ ᴜsᴀɢᴇ :-** `/getstate CountryName`"
            )
            await message.reply_text(usage_text)
            return

        country_name = message.text.split(None, 1)[1]
        country = None
        for c in pycountry.countries:
            if country_name.lower() in [c.name.lower(), getattr(c, "official_name", "").lower()]:
                country = c
                break

        if not country:
            await message.reply_text("**⋟ ɴᴏ sᴜᴄʜ ᴄᴏᴜɴᴛʀʏ ғᴏᴜɴᴅ.**")
            return

        subdivisions = list(pycountry.subdivisions.get(country_code=country.alpha_2))
        if not subdivisions:
            await message.reply_text("**⋟ ɴᴏ sᴛᴀᴛᴇs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜɪs ᴄᴏᴜɴᴛʀʏ.**")
            return

        states_text = "\n".join([f"**⊚** {sub.name}" for sub in subdivisions])
        total = len(subdivisions)

        final_text = (
            f"**✦ sᴛᴀᴛᴇs ɪɴ :-** {country.name}\n\n"
            f"{states_text}\n\n"
            f"**⋟ ᴛᴏᴛᴀʟ sᴛᴀᴛᴇs:** `{total}`\n\n"
            f"**⋟ ʙʏ :- {app.mention}**"
        )

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
        )

        await message.reply_text(final_text, reply_markup=buttons)

    except Exception as e:
        await message.reply_text(f"**⋟ ᴇʀʀᴏʀ :-** `{str(e)}`")
    


@app.on_message(filters.command("phone"))
async def check_phone(client, message):
    try:
        if len(message.text.split()) < 2:
            usage_text = (
                "**⋟ ᴜsᴀɢᴇ :-** `/phone +91××××××××`"
            )
            return await send_message(message, usage_text)

        number = message.text.split(None, 1)[1]
        key = "f66950368a61ebad3cba9b5924b4532d"
        api = f"http://apilayer.net/api/validate?access_key={key}&number={number}&country_code=&format=1"

        output = requests.get(api)
        obj = json.loads(output.text)

        if not obj.get("valid"):
            return await send_message(message, f"**⋟ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ :-** `{number}`")

        g = (
            f"**🔍 ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴄʜᴇᴄᴋᴇʀ**\n\n"
            f"**⋟ ᴠᴀʟɪᴅ :-** `{obj['valid']}`\n"
            f"**⋟ ɴᴜᴍʙᴇʀ :-** `{number}`\n"
            f"**⋟ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ :-** `{obj['country_code']}`\n"
            f"**⋟ ᴄᴏᴜɴᴛʀʏ ɴᴀᴍᴇ :-** `{obj['country_name']}`\n"
            f"**⋟ ʟᴏᴄᴀᴛɪᴏɴ :-** `{obj['location']}`\n"
            f"**⋟ ᴄᴀʀʀɪᴇʀ :-** `{obj['carrier']}`\n"
            f"**⋟ ᴅᴇᴠɪᴄᴇ ᴛʏᴘᴇ :-** `{obj['line_type']}`\n\n"
            f"**⋟ ʙʏ :- {app.mention}**"
        )

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙",
                                   url=f"https://t.me/{app.username}?startgroup=true")]]
        )

        await send_message(message, g, keyboard)

    except Exception as e:
        await send_message(message, f"**⋟ ᴇʀʀᴏʀ:** `{str(e)}`")
