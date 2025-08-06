from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SONALI_MUSIC import app

@app.on_message(filters.command("privacy"))
async def privacy_command(client: Client, message: Message):
    await message.reply_photo(
        photo="https://files.catbox.moe/0jpf7u.jpg",
        caption="**➻ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘᴜʀᴠɪ ʙᴏᴛꜱ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ.**\n\n**⊚ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛʜᴇɴ ꜱᴇᴇ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ 🔏**",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("˹ ᴘʀɪᴠᴀᴄʏ ˼", url="https://telegra.ph/Privacy-Policy--Purvi-Bots-by-ALPHA-BABY-08-06")]
            ]
        )
    )
