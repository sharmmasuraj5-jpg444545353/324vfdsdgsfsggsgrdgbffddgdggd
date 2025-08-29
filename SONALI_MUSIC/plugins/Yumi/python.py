from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import traceback
import io, os
import sys
import requests
import aiohttp
import json
from typing import Tuple
from SONALI_MUSIC import app

BUTTON_ADD = InlineKeyboardMarkup(
    [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{app.username}?startgroup=true")]]
)


def check_python_syntax(code: str) -> Tuple[bool, str]:
    try:
        compile(code, "<string>", "exec")
        return True, None
    except SyntaxError as e:
        err_line = e.text.strip() if e.text else ""
        return False, f"{e.msg} at line {e.lineno}, column {e.offset}\n{err_line}"

async def safe_reply_message(message: Message, text: str, max_length: int = 4096):
    """Safely reply with text, splitting long messages into multiple parts"""
    if len(text) <= max_length:
        return await message.reply(text, quote=True, reply_markup=BUTTON_ADD)
    
    # Split long message into parts (4096 characters max per message)
    parts = []
    current_part = ""
    
    # Smart splitting to avoid breaking code blocks
    lines = text.split('\n')
    for line in lines:
        if len(current_part) + len(line) + 1 > max_length:
            if current_part:
                parts.append(current_part)
                current_part = line
            else:
                # If single line is too long, split it
                for i in range(0, len(line), max_length - 100):
                    parts.append(line[i:i + max_length - 100])
        else:
            if current_part:
                current_part += '\n' + line
            else:
                current_part = line
    
    if current_part:
        parts.append(current_part)
    
    # Send first part with reply and buttons
    first_message = await message.reply(
        parts[0], 
        quote=True, 
        reply_markup=BUTTON_ADD if len(parts) == 1 else None
    )
    
    # Send remaining parts as follow-up messages
    for i, part in enumerate(parts[1:], 2):
        await message.reply(
            f"**ᴘᴀʀᴛ {i} :-**\n{part}",
            quote=False
        )

@app.on_message(filters.command("syntax"))
async def syntax_func(client: Client, message: Message):
    # Extract code text from reply or command
    if message.reply_to_message:
        if message.reply_to_message.text:
            code_text = message.reply_to_message.text
        elif message.reply_to_message.document:
            doc = message.reply_to_message.document
            if not doc.file_name.endswith((".txt", ".py")):
                return await message.reply("**❌ ᴏɴʟʏ ᴘʏᴛʜᴏɴ/ᴛᴇxᴛ ғɪʟᴇs ᴀʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ.**")
            file_path = await message.reply_to_message.download()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code_text = f.read()
            except Exception as e:
                return await message.reply(f"**❌ ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴀᴅ ғɪʟᴇ :-**\n\n```{e}```")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            return await message.reply("**❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʏᴛʜᴏɴ ᴄᴏᴅᴇ ᴏʀ ᴛᴇxᴛ ғɪʟᴇ.**")
    else:
        if len(message.command) < 2:
            return await message.reply(
                "**⚡ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʏᴛʜᴏɴ ᴄᴏᴅᴇ ᴏʀ ɢɪᴠᴇ ᴄᴏᴅᴇ ᴡɪᴛʑ ᴄᴏᴍᴍᴀɴᴅ :-**\n\n`/syntax <code>`"
            )
        code_text = message.text.split(None, 1)[1]

    # Check syntax
    ok, error = check_python_syntax(code_text)

    if ok:
        response_text = f"**✅ ᴄᴏᴅᴇ sʏɴᴛᴀx ʟᴏᴏᴋs ғɪɴᴇ !**\n\n```\n{code_text}\n```"
    else:
        response_text = f"**❌ sʏɴᴛᴀx ᴇʀʀᴏʀ :-**\n```\n{error}\n```"

    # Use safe reply function to handle long messages
    await safe_reply_message(message, response_text)
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
