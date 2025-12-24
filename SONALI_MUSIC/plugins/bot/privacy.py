from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SONALI_MUSIC import app

@app.on_message(filters.command("privacy"))
async def privacy_command(client: Client, message: Message):
    await message.reply_photo(
        photo="https://files.catbox.moe/0jpf7u.jpg",
        caption="**➻ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ �꯭꯭𝐇͟ᴇ꯭𝐗꯭͟ᴀ꯭ɴ꯭ᴇ꯭Ʀ꯭ᴠ꯭ᴇ꯭𝆺꯭𝅥🎭  ʙᴏᴛꜱ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ.**\n\n**⊚ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛʜᴇɴ ꜱᴇᴇ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ 🔏**",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("˹ ᴘʀɪᴠᴀᴄʏ ˼", url="https://graph.org/PRIVACY-POLICY--HEXANERVE-BOTS-12-24")]
            ]
        )
    )
