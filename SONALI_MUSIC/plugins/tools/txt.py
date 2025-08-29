import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from SONALI_MUSIC import app


def save_message_to_txt(message_text: str, filename: str = "messages.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(message_text + "\n")

@app.on_message(filters.reply & filters.command("txt"))
async def save_replied_message(client: Client, message: Message):
    try:
        replied_message = message.reply_to_message
        if replied_message and replied_message.text:
            save_message_to_txt(replied_message.text)
            
            # Create the caption with bot mention
            caption = (
                "**┏━━━━━━━⍟**\n"
                "**┃ ʜᴇʀᴇ ɪs ʏᴏᴜʀ .ᴛxᴛ ғɪʟᴇ ✅**\n"
                "**┗━━━━━━━━━━━━━━━⊛**\n\n"
                f"**⊙ ɢᴇɴ ʙʏ :- {app.mention}**"
            )
            
            # Create inline keyboard with group button
            keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙",
                           url=f"https://t.me/{app.username}?startgroup=true")]]
)
            
            # Send the messages.txt file to the user with the specified caption
            if os.path.exists("messages.txt"):
                await message.reply_document(
                    "messages.txt", 
                    caption=caption,
                    reply_markup=keyboard
                )
            
            # Delete the messages.txt file after sending it
            os.remove("messages.txt")
        else:
            await message.reply_text("**⋟ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴛᴏ sᴀᴠᴇ ɪᴛ.**")
            
    except Exception as e:
        await message.reply_text(f"**⋟ ᴇʀʀᴏʀ:** `{str(e)}`")
