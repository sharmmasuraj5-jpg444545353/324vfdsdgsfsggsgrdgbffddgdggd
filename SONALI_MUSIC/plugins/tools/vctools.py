from pyrogram import Client, filters
from pyrogram.types import Message
from SONALI_MUSIC import app
from config import OWNER_ID
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# vc on
@app.on_message(filters.video_chat_started)
async def brah(_, msg):
    text = "**🫣 ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ 😆**"
    add_link = f"https://t.me/{app.username}?startgroup=true"
    reply_text = f"{text}"

    # Inline Keyboard with a button to add the bot
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="๏ ᴊσɪη ᴠᴄ ๏", url=add_link)]
    ])

    # Send the message with the keyboard
    await msg.reply(reply_text, reply_markup=reply_markup)


# vc off
@app.on_message(filters.video_chat_ended)
async def brah2(_, msg: Message):
    text = "**😤 ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ 🙁**"
    add_link = f"https://t.me/{app.username}?startgroup=true"
    reply_text = f"{text}"

    # Inline Keyboard with a button to add the bot
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="๏ ᴧᴅᴅ ϻє вᴧвყ ๏", url=add_link)]
    ])

    # Send the message with the keyboard
    await msg.reply(reply_text, reply_markup=reply_markup)
    

# invite members on vc
@app.on_message(filters.video_chat_members_invited)
async def brah3(app: app, message: Message):
    text = f"➠ {message.from_user.mention}\n\n**๏ ɪɴᴠɪᴛɪɴɢ ɪɴ ᴠᴄ ᴛᴏ ๏**\n\n**➠ **"
    x = 0
    for user in message.video_chat_members_invited.users:
        try:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
            x += 1
        except Exception:
            pass

    try:
        invite_link = await app.export_chat_invite_link(message.chat.id)
        add_link = f"https://t.me/{app.username}?startgroup=true"
        reply_text = f"{text} 🤭🤭"

        await message.reply(reply_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text= "๏ ᴊσɪη ᴠᴄ ๏", url=add_link)],
        ]))
    except Exception as e:
        print(f"Error: {e}")


####

from sympy import sympify

@app.on_message(filters.command("math", prefixes="/"))
async def calculate_math(client, message):
    if len(message.text.split(" ", 1)) < 2:
        await message.reply("❍ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴀᴛʜᴇᴍᴀᴛɪᴄᴀʟ ᴇxᴘʀᴇssɪᴏɴ ᴀғᴛᴇʀ /math.")
        return

    expression = message.text.split(" ", 1)[1]
    try:
        # Safely evaluate the mathematical expression
        result = sympify(expression)
        response = f"ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs : {result}"
    except Exception as e:
        response = f"❍ ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ. ᴇʀʀᴏʀ: {str(e)}"
    
    await message.reply(response)
    
