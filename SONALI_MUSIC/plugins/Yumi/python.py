from pyrogram import Client, filters
from pyrogram.types import Message
import traceback
import io
import sys
from SONALI_MUSIC import app

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
        # Redirect stdout to capture prints
        sys.stdout = str_io
        local_vars = {}
        exec(python_code, {}, local_vars)
        sys.stdout = sys.__stdout__  # Reset stdout

        output = str_io.getvalue()
        if not output.strip():
            output = "✅ ᴄᴏᴅᴇ ᴇxᴇᴄᴜᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ. (ɴᴏ ᴏᴜᴛᴘᴜᴛ)"
        else:
            output = f"✅ ᴄᴏᴅᴇ ᴇxᴇᴄᴜᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ:\n```\n{output}\n```"

        await message.reply(output)

    except Exception:
        sys.stdout = sys.__stdout__  # Reset stdout in case of error
        traceback_str = traceback.format_exc()
        await message.reply(f"❌ ᴄᴏᴅᴇ ᴇxᴇᴄᴜᴛɪᴏɴ ᴇʀʀᴏʀ:\n```\n{traceback_str}\n```")
