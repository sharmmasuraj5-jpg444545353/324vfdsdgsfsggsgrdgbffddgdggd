import random
import asyncio
from SONALI_MUSIC import app
from pyrogram import filters
from pyrogram.types import Message
from pymongo import MongoClient
from config import MONGO_DB_URI 

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["welcome_db"]
chat_settings = db["chat_settings"]

PURVI_WEL_MSG = [
    "❖ ʜᴇʏ {user}, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!",
    "❖ ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ ʜᴇʀᴇ, {user}!",
    "❖ ɢʀᴇᴇᴛɪɴɢs {user}! ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.",
    "❖ ʜᴇʟʟᴏ {user}! ᴍᴀᴋᴇ ʏᴏᴜʀsᴇʟꜰ ᴀᴛ ʜᴏᴍᴇ.",
    "❖ ᴡᴇʟᴄᴏᴍᴇ {user}! ʜᴏᴘᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴀ ɢʀᴇᴀᴛ ᴛɪᴍᴇ.",
    "❖ ʜɪ {user}, ʜᴀᴘᴘʏ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ ʜᴇʀᴇ!",
    "❖ ᴄʜᴇᴇʀs {user}, ᴡᴇʟᴄᴏᴍᴇ ᴀʙᴏᴀʀᴅ!",
    "❖ {user}, ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ!",
    "❖ ʜᴇʏ {user}, ᴍᴀᴋᴇ ʏᴏᴜʀsᴇʟꜰ ᴄᴏᴍꜰᴏʀᴛᴀʙʟᴇ!",
    "❖ ᴡᴇʟᴄᴏᴍᴇ {user}! ʟᴇᴛ's ʜᴀᴠᴇ ꜰᴜɴ ᴛᴏɢᴇᴛʜᴇʀ!",
    "❖ ʜᴇʟʟᴏ {user}, ɪᴛ's ɢʀᴇᴀᴛ ᴛᴏ sᴇᴇ ʏᴏᴜ!",
    "❖ ɢʟᴀᴅ ʏᴏᴜ'ʀᴇ ʜᴇʀᴇ, {user}!",
    "❖ ᴡᴇʟᴄᴏᴍᴇ {user}! ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ ᴄʜᴀᴛ!",
    "❖ ʜᴇʏ {user}, ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ!",
    "❖ {user}, ᴡᴇʟᴄᴏᴍᴇ! ᴍᴀᴋᴇ ɴᴇᴡ ꜰʀɪᴇɴᴅs!",
    "❖ ʜᴇʟʟᴏ {user}, ʜᴏᴘᴇ ʏᴏᴜ ᴇɴᴊᴏʏ ʜᴇʀᴇ!",
    "❖ ᴡᴇʟᴄᴏᴍᴇ {user}! ᴊᴏɪɴ ᴛʜᴇ ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴ!",
    "❖ ʜɪ {user}, ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴛɪᴍᴇ ʜᴇʀᴇ!",
    "❖ ᴄʜᴇᴇʀs {user}! ɢʟᴀᴅ ʏᴏᴜ ᴊᴏɪɴᴇᴅ!",
    "❖ {user}, ᴡᴇʟᴄᴏᴍᴇ! ʟᴇᴛ's ʜᴀᴠᴇ ꜰᴜɴ!"
]


PURVI_LEFT_MSG = [
    "❖ ʙʏᴇ ʙʏᴇ {user}! sᴇᴇ ʏᴏᴜ sᴏᴏɴ.",
    "❖ {user} ʟᴇꜰᴛ... ᴛʜᴇ ɢʀᴏᴜᴘ ꜰᴇᴇʟs ᴇᴍᴘᴛʏ.",
    "❖ ɢᴏᴏᴅʙʏᴇ {user}! ᴛᴀᴋᴇ ᴄᴀʀᴇ.",
    "❖ {user} ɪs ɢᴏɴᴇ, ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ!",
    "❖ sᴇᴇ ʏᴏᴜ ʟᴀᴛᴇʀ {user}!",
    "❖ {user} ʟᴇꜰᴛ, ʜᴏᴘᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ ʙᴀᴄᴋ!",
    "❖ ꜰᴀʀᴇᴡᴇʟʟ {user}! ᴛᴀᴋᴇ ᴄᴀʀᴇ!",
    "❖ {user} ᴇxɪᴛᴇᴅ... ɢᴏᴏᴅ ʟᴜᴄᴋ!",
    "❖ sᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ ɢᴏ {user}!",
    "❖ {user} ʟᴇꜰᴛ ᴛʜᴇ ɢʀᴏᴜᴘ.",
    "❖ ʙʏᴇ {user}! ᴄᴏᴍᴇ ʙᴀᴄᴋ sᴏᴏɴ!",
    "❖ {user} ʜᴀs ʟᴇꜰᴛ... ᴛɪʟʟ ɴᴇxᴛ ᴛɪᴍᴇ!",
    "❖ {user} ɪs ɢᴏɴᴇ, sᴇᴇ ʏᴏᴜ sᴏᴏɴ!",
    "❖ ɢᴏᴏᴅʙʏᴇ {user}! sᴛᴀʏ sᴀғᴇ!",
    "❖ {user} ʟᴇꜰᴛ, ʜᴏᴘᴇ ʏᴏᴜ ʀᴇᴛᴜʀɴ sᴏᴏɴ!",
    "❖ ʙʏᴇ {user}! ɪᴛ ᴡᴀs ɴɪᴄᴇ ʜᴀᴠɪɴɢ ʏᴏᴜ!",
    "❖ {user} ᴇxɪᴛᴇᴅ... ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ!",
    "❖ sᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ ʟᴇᴀᴠᴇ {user}!",
    "❖ {user} ʟᴇꜰᴛ, ᴛᴀᴋᴇ ᴄᴀʀᴇ!",
    "❖ sᴇᴇ ʏᴏᴜ ʟᴀᴛᴇʀ {user}!"
]


last_welcome = {}

def is_welcome_enabled(chat_id):
    setting = chat_settings.find_one({"chat_id": chat_id})
    return setting.get("welcome", True) if setting else True

def is_left_enabled(chat_id):
    setting = chat_settings.find_one({"chat_id": chat_id})
    return setting.get("left", True) if setting else True

def set_welcome(chat_id, value: bool):
    chat_settings.update_one({"chat_id": chat_id}, {"$set": {"welcome": value}}, upsert=True)

def set_left(chat_id, value: bool):
    chat_settings.update_one({"chat_id": chat_id}, {"$set": {"left": value}}, upsert=True)


@app.on_message(filters.command(["welcome"]) & filters.group)
async def welcome_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❖ usage: /welcome on or /welcome off")
    action = message.command[1].lower()
    if action == "on":
        set_welcome(message.chat.id, True)
        await message.reply_text("❖ welcome messages enabled!")
    elif action == "off":
        set_welcome(message.chat.id, False)
        await message.reply_text("❖ welcome messages disabled!")
    else:
        await message.reply_text("❖ usage: /welcome on or /welcome off")


@app.on_message(filters.command(["left"]) & filters.group)
async def left_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❖ usage: /left on or /left off")
    action = message.command[1].lower()
    if action == "on":
        set_left(message.chat.id, True)
        await message.reply_text("❖ left messages enabled!")
    elif action == "off":
        set_left(message.chat.id, False)
        await message.reply_text("❖ left messages disabled!")
    else:
        await message.reply_text("❖ usage: /left on or /left off")


@app.on_message(filters.new_chat_members)
async def welcome(client, message: Message):
    if not is_welcome_enabled(message.chat.id):
        return

    chat_id = message.chat.id

    # Delete previous welcome if exists
    if chat_id in last_welcome:
        try:
            await client.delete_messages(chat_id, last_welcome[chat_id])
        except:
            pass

    for new_member in message.new_chat_members:
        text = random.choice(PURVI_WEL_MSG).format(user=new_member.mention)
        sent = await message.reply_text(text)
        last_welcome[chat_id] = sent.message_id

@app.on_message(filters.left_chat_member)
async def left(client, message: Message):
    if not is_left_enabled(message.chat.id):
        return

    left_user = message.left_chat_member
    text = random.choice(PURVI_LEFT_MSG).format(user=left_user.mention)
    sent = await message.reply_text(text)

    # Auto delete after 10 seconds
    await asyncio.sleep(10)
    try:
        await client.delete_messages(message.chat.id, sent.message_id)
    except:
        pass
