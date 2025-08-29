from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import qrcode
from SONALI_MUSIC import app
import io


def generate_qr_code(text: str) -> io.BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


@app.on_message(filters.command("qr"))
async def qr_handler(client: Client, message: Message):
    if len(message.command) > 1:
        input_text = " ".join(message.command[1:])
        qr_image = generate_qr_code(input_text)
        
        # Create caption with bot mention
        caption = (
            "**⋟ ʜᴇʀᴇ's ʏᴏᴜʀ ǫʀ ᴄᴏᴅᴇ ✦**\n\n"
            f"**⊙ ɢᴇɴ ʙʏ :- {app.mention}**"
        )
        
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{app.username}?startgroup=true")]
            ]
        )
        
        await message.reply_photo(qr_image, caption=caption, reply_markup=keyboard)
    else:
        await message.reply_text(
            "**⋟ ᴜsᴀɢᴇ :-** `/qr Your Text`"
)
