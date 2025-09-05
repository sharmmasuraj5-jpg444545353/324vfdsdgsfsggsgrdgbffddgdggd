from pyrogram import filters
from SONALI_MUSIC import app


@app.on_message(filters.command("st"))
async def generate_sticker(client, message):
    if len(message.command) == 2:
        sticker_id = message.command[1]
        try:
            await client.send_sticker(message.chat.id, sticker=sticker_id)
        except Exception as e:
            await message.reply_text(f"**ᴇʀʀᴏʀ :-** `{e}`")
    else:
        await message.reply_text(
            "**ᴘʀᴏᴠɪᴅᴇ ᴀ sᴛɪᴄᴋᴇʀ ɪᴅ ᴀғᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**\n\n"
            "**ᴜsᴀɢᴇ :-** `/st <sticker_id>`"
        )
