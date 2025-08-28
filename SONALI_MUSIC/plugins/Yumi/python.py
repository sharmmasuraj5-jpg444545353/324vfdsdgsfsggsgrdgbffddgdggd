from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import traceback
import io
import sys
import requests
import aiohttp
import json
from SONALI_MUSIC import app

BUTTON_ADD = InlineKeyboardMarkup(
    [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
)

@app.on_message(filters.command("python"))
async def execute_python_code(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply(
            "**⋟ ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʏᴛʜᴏɴ ᴄᴏᴅᴇ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.**\n\n"
            "**ᴜsᴀɢᴇ :-** `/python print('hello, world!')`"
        )
        return

    python_code = " ".join(message.command[1:])
    str_io = io.StringIO()
    try:
        sys.stdout = str_io
        local_vars = {}
        exec(python_code, {}, local_vars)
        sys.stdout = sys.__stdout__

        output = str_io.getvalue()
        if not output.strip():
            output = "**✅ ᴄᴏᴅᴇ ᴇxᴇᴄᴜᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ. (ɴᴏ ᴏᴜᴛᴘᴜᴛ)**"
        else:
            output = f"**✅ ᴄᴏᴅᴇ ᴇxᴇᴄᴜᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ :-**\n\n```\n{output}\n```"

        await message.reply(output, reply_markup=BUTTON_ADD)

    except Exception:
        sys.stdout = sys.__stdout__
        traceback_str = traceback.format_exc()
        await message.reply(
            f"**❌ ᴄᴏᴅᴇ ᴇxᴇᴄᴜᴛɪᴏɴ ᴇʀʀᴏʀ :-**\n\n```\n{traceback_str}\n```",
            reply_markup=BUTTON_ADD
        )

@app.on_message(filters.command("print"))
async def print_code(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        usage_text = (
            "⚠️ **ᴜsᴀɢᴇ :** `/print <code>` **ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ `/print`**"
        )
        await message.reply_text(usage_text)
        return

    code_text = message.reply_to_message.text if message.reply_to_message else " ".join(message.command[1:])
    response_text = f"**⋟ ꜱᴜᴄᴄᴇssꜰᴜʟʟʏ ᴘʀɪɴᴛᴇᴅ :-**\n\n```\n{code_text}\n```"
    await message.reply_text(response_text, reply_markup=BUTTON_ADD)

# Fixed async version of get_pypi_info
async def get_pypi_info(package_name):
    try:
        api_url = f"https://pypi.org/pypi/{package_name}/json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    pypi_info = await response.json()
                    return pypi_info
                else:
                    print(f"**⋟ ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ᴘʏᴘɪ ɪɴғᴏʀᴍᴀᴛɪᴏɴ :-** HTTP {response.status}")
                    return None
    
    except Exception as e:
        print(f"**⋟ ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ᴘʏᴘɪ ɪɴғᴏʀᴍᴀᴛɪᴏɴ :-** {e}")
        return None

@app.on_message(filters.command("pypi", prefixes="/"))
async def pypi_info_command(client: Client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "**⋟ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘᴀᴄᴋᴀɢᴇ ɴᴀᴍᴇ.**\n\n**ᴜsᴀɢᴇ :/** `/pypi package_name`"
        )
        return

    package_name = message.command[1]
    temp_msg = await message.reply_text(f"**⋟ ꜰᴇᴛᴄʜɪɴɢ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ꜰᴏʀ '{package_name}'...**")

    pypi_info = await get_pypi_info(package_name)

    if pypi_info:
        info = pypi_info.get("info", {})
        project_url = info.get("project_urls", {}).get("Homepage", "N/A")

        response_text = (
            f"**⋟ ᴘᴀᴄᴋᴀɢᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ :-**\n\n"
            f"**➤ ɴᴀᴍᴇ :-** `{info.get('name', 'N/A')}`\n"
            f"**➤ ʟᴀᴛᴇsᴛ ᴠᴇʀsɪᴏɴ :-** `{info.get('version', 'N/A')}`\n"
            f"**➤ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ :-** `{info.get('summary', 'N/A')}`\n"
            f"**➤ ᴘʀᴏᴊᴇᴄᴛ ᴜʀʟ :-** [ʟɪɴᴋ]({project_url})"
        )
    else:
        response_text = "⚠️ **ғᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ғʀᴏᴍ ᴘʏᴘɪ.**"

    await temp_msg.delete()
    await message.reply_text(response_text, reply_markup=BUTTON_ADD, disable_web_page_preview=True)
