from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SONALI_MUSIC import app
from config import BOT_USERNAME
from SONALI_MUSIC.utils.errors import capture_err
import httpx 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_txt = """**<u>❃ ᴡєʟᴄσϻє ᴛᴏ ᴛєᴧϻ ᴘᴜʀᴠɪ ʀєᴘσs ❃</u>

✼ ʀєᴘᴏ ᴛᴏ ηʜɪ ϻɪʟєɢᴧ ʏʜᴧ
 
❉ ᴘᴧʜʟє ᴘᴧᴘᴧ ʙσʟ ʀєᴘᴏ ᴏᴡηєʀ ᴋᴏ 

✼ || [ᴧʟᴘʜᴧ-ʙᴧʙʏ](https://t.me/ll_ALPHA_BABY_lll) ||
 
❊ ʀᴜη 24x7 ʟᴧɢ ϝʀєє ᴡɪᴛʜσᴜᴛ sᴛσᴘ**
"""




@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("✙ ᴧᴅᴅ ϻє вᴧʙʏ ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
          InlineKeyboardButton("• ʜєʟᴘ •", url="https://t.me/+gMy8Cp190ediNzZl"),
          InlineKeyboardButton("• 𝛅ᴜᴘᴘσʀᴛ •", url="https://t.me/PURVI_SUPPORT"),
          ],
[
InlineKeyboardButton("• ϻᴧɪη ʙσᴛ •", url=f"https://t.me/PURVI_MUSIC_ROBOT"),

        ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://files.catbox.moe/kbi6t5.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
