from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json
import pycountry
from SONALI_MUSIC import app


# 📌 Common send message function (async)
async def send_message(message, text, reply_markup=None):
    await message.reply_text(text, reply_markup=reply_markup)


# 🌍 STATES FETCHER with Pagination
@app.on_message(filters.command("getstate"))
async def get_states(client, message):
    try:
        if len(message.text.split()) < 2:
            usage_text = (
                "**⋟ ᴜsᴀɢᴇ:** `/getstate CountryName`\n"
                "**⋟ ᴇxᴀᴍᴘʟᴇ:** `/getstate India`\n"
                "**⋟ ᴇxᴀᴍᴘʟᴇ:** `/getstate United States`"
            )
            return await send_message(message, usage_text)

        country_name = message.text.split(" ", 1)[1]
        country = pycountry.countries.get(name=country_name)

        if not country:
            for c in pycountry.countries:
                if country_name.lower() in c.name.lower():
                    country = c
                    break

        if country:
            states = list(pycountry.subdivisions.get(country_code=country.alpha_2))
            if states:
                # Default page = 0
                await send_states_page(message, country.name, states, 0)
            else:
                await send_message(message, f"**⋟ ɴᴏ sᴛᴀᴛᴇs ғᴏᴜɴᴅ ғᴏʀ {country.name}**\n\nBy :- {app.me.mention}")
        else:
            await send_message(message, f"**⋟ ᴄᴏᴜɴᴛʀʏ ɴᴏᴛ ғᴏᴜɴᴅ:** `{country_name}`\n\nBy :- {app.me.mention}")

    except Exception as e:
        await send_message(message, f"**⋟ ᴇʀʀᴏʀ:** `{str(e)}`\n\nBy :- {app.me.mention}")


# Helper: send paginated states
async def send_states_page(message, country_name, states, page):
    per_page = 20
    start = page * per_page
    end = start + per_page
    subset = states[start:end]

    text = f"**⋟ sᴛᴀᴛᴇs ᴏғ {country_name}: (Page {page+1})**\n\n"
    text += "\n".join([f"⋟ {state.name}" for state in subset])
    text += f"\n\nBy :- {app.me.mention}"

    buttons = []
    if start > 0:
        buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"states:{country_name}:{page-1}"))
    if end < len(states):
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"states:{country_name}:{page+1}"))

    keyboard = InlineKeyboardMarkup([buttons] + [
        [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙",
                              url=f"https://t.me/{app.username}?startgroup=true")]
    ])

    await message.reply_text(text, reply_markup=keyboard)


# Callback query handler for states pagination
@app.on_callback_query(filters.regex(r"^states:"))
async def states_callback(client, callback_query):
    _, country_name, page = callback_query.data.split(":")
    country = pycountry.countries.get(name=country_name)
    if not country:
        for c in pycountry.countries:
            if country_name.lower() in c.name.lower():
                country = c
                break
    if country:
        states = list(pycountry.subdivisions.get(country_code=country.alpha_2))
        await callback_query.message.delete()
        await send_states_page(callback_query.message, country.name, states, int(page))


# 📱 PHONE CHECKER using Numverify API
@app.on_message(filters.command("phone"))
async def check_phone(client, message):
    try:
        if len(message.text.split()) < 2:
            usage_text = (
                "**⋟ ᴜsᴀɢᴇ:** `/phone +919876543210`\n"
                "**⋟ ᴇxᴀᴍᴘʟᴇ:** `/phone +1234567890`"
            )
            return await send_message(message, usage_text)

        number = message.text.split(None, 1)[1]
        key = "YOUR_NUMVERIFY_API_KEY"  # 🔑 Replace with real API key
        api = f"http://apilayer.net/api/validate?access_key={key}&number={number}&country_code=&format=1"

        output = requests.get(api)
        obj = json.loads(output.text)

        if not obj.get("valid"):
            return await send_message(message, f"**⋟ Invalid Number:** `{number}`\n\nBy :- {app.me.mention}")

        g = (
            f"**🔍 ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴄʜᴇᴄᴋᴇʀ**\n\n"
            f"**⋟ ᴠᴀʟɪᴅ:** `{obj['valid']}`\n"
            f"**⋟ ɴᴜᴍʙᴇʀ:** `{number}`\n"
            f"**⋟ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ:** `{obj['country_code']}`\n"
            f"**⋟ ᴄᴏᴜɴᴛʀʏ ɴᴀᴍᴇ:** `{obj['country_name']}`\n"
            f"**⋟ ʟᴏᴄᴀᴛɪᴏɴ:** `{obj['location']}`\n"
            f"**⋟ ᴄᴀʀʀɪᴇʀ:** `{obj['carrier']}`\n"
            f"**⋟ ᴅᴇᴠɪᴄᴇ ᴛʏᴘᴇ:** `{obj['line_type']}`\n\n"
            f"By :- {app.me.mention}"
        )

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙",
                                   url=f"https://t.me/{app.username}?startgroup=true")]]
        )

        await send_message(message, g, keyboard)

    except Exception as e:
        await send_message(message, f"**⋟ ᴇʀʀᴏʀ:** `{str(e)}`\n\nBy :- {app.me.mention}")
