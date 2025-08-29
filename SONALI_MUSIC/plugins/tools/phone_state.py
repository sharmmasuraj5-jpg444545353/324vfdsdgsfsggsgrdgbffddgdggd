from pyrogram import Client, filters
import requests
import json
import pycountry
from SONALI_MUSIC import app
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def send_message(message, text, reply_markup=None):
    message.reply_text(text, reply_markup=reply_markup)


# 📱 PHONE CHECKER
@app.on_message(filters.command("phone"))
def check_phone(client, message):
    try:
        # Check if number is provided
        if len(message.text.split()) < 2:
            usage_text = (
                "**⋟ ᴜsᴀɢᴇ:** `/phone +919876543210`\n"
                "**⋟ ᴇxᴀᴍᴘʟᴇ:** `/phone +1234567890`"
            )
            return send_message(message, usage_text)
            
        args = message.text.split(None, 1)
        number = args[1]
        key = "f66950368a61ebad3cba9b5924b4532d"
        api = f"http://apilayer.net/api/validate?access_key={key}&number={number}&country_code=&format=1"

        output = requests.get(api)
        obj = json.loads(output.text)

        validornot = obj["valid"]
        country_code = obj["country_code"]
        country_name = obj["country_name"]
        location = obj["location"]
        carrier = obj["carrier"]
        line_type = obj["line_type"]

        g = (
            f"**🔍 ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴄʜᴇᴄᴋᴇʀ**\n\n"
            f"**⋟ ᴠᴀʟɪᴅ:** `{validornot}`\n"
            f"**⋟ ɴᴜᴍʙᴇʀ:** `{number}`\n"
            f"**⋟ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ:** `{country_code}`\n"
            f"**⋟ ᴄᴏᴜɴᴛʀʏ ɴᴀᴍᴇ:** `{country_name}`\n"
            f"**⋟ ʟᴏᴄᴀᴛɪᴏɴ:** `{location}`\n"
            f"**⋟ ᴄᴀʀʀɪᴇʀ:** `{carrier}`\n"
            f"**⋟ ᴅᴇᴠɪᴄᴇ ᴛʏᴘᴇ:** `{line_type}`"
        )
        
        # Create inline keyboard with group button
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✨ ᴊᴏɪɴ ᴏᴜʀ ɢʀᴏᴜᴘ", url="https://t.me/YourGroupLink")],
                [InlineKeyboardButton("🌟 ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ", url="https://t.me/YourSupportChat")]
            ]
        )
        
        send_message(message, g, keyboard)

    except Exception as e:
        send_message(message, f"**⋟ ᴇʀʀᴏʀ:** `{str(e)}`")


# 🌍 STATES FETCHER
@app.on_message(filters.command("getstate"))
def get_states(client, message):
    try:
        # Check if country name is provided
        if len(message.text.split()) < 2:
            usage_text = (
                "**⋟ ᴜsᴀɢᴇ:** `/getstate CountryName`\n"
                "**⋟ ᴇxᴀᴍᴘʟᴇ:** `/getstate India`\n"
                "**⋟ ᴇxᴀᴍᴘʟᴇ:** `/getstate United States`"
            )
            return send_message(message, usage_text)
            
        country_name = message.text.split(" ", 1)[1]
        country = pycountry.countries.get(name=country_name)
        
        if not country:
            # Try searching by common name or other attributes
            for c in pycountry.countries:
                if country_name.lower() in c.name.lower():
                    country = c
                    break
            
        if country:
            states = pycountry.subdivisions.get(country_code=country.alpha_2)
            
            if states:
                states_list = [f"⋟ {state.name}" for state in list(states)[:20]]  # Limit to first 20 states
                states_message = f"**⋟ sᴛᴀᴛᴇs ᴏғ {country.name}:**\n\n" + "\n".join(states_list)
                
                # Add note if there are more states
                if len(list(states)) > 20:
                    states_message += f"\n\n**⋟ ...ᴀɴᴅ {len(list(states)) - 20} ᴍᴏʀᴇ sᴛᴀᴛᴇs**"
            else:
                states_message = f"**⋟ ɴᴏ sᴛᴀᴛᴇs ғᴏᴜɴᴅ ғᴏʀ {country.name}**"
        else:
            states_message = f"**⋟ ᴄᴏᴜɴᴛʀʏ ɴᴏᴛ ғᴏᴜɴᴅ:** `{country_name}`"

        # Create inline keyboard with group button
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✨ ᴊᴏɪɴ ᴏᴜʀ ɢʀᴏᴜᴘ", url="https://t.me/YourGroupLink")],
                [InlineKeyboardButton("🌟 ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ", url="https://t.me/YourSupportChat")]
            ]
        )
        
        send_message(message, states_message, keyboard)

    except Exception as e:
        send_message(message, f"**⋟ ᴇʀʀᴏʀ:** `{str(e)}`")
