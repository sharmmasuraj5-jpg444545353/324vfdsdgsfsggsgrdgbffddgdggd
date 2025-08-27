import asyncio
import random
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pymongo import MongoClient
from config import MONGO_DB_URI

from SONALI_MUSIC import app

# MongoDB setup
mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["welcome_db"]
welc = db["welcome"]

# Welcome messages list
PURVI_WEL_MSG = [
    "❖ ʜᴇʏ {user}, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {chat}!",
    "✿ {user}, ɪ'ᴍ ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ ʜᴇʀᴇ ɪɴ {chat}.",
    "✧ {user} ᴊᴜsᴛ ʟᴀɴᴅᴇᴅ ɪɴ {chat}, ᴡᴇʟᴄᴏᴍᴇ!",
]

PURVI_LEFT_MSG = [
    "✦ {user} ʟᴇғᴛ {chat}, sᴇᴇ ʏᴏᴜ ᴀɢᴀɪɴ!",
    "❖ {user} ɪs ɴᴏ ʟᴏɴɢᴇʀ ᴡɪᴛʜ ᴜs ɪɴ {chat}.",
    "✿ ɢᴏᴏᴅʙʏᴇ {user}, ғʀᴏᴍ {chat}!",
]


# ─────────────── Helper: Admin Check ─────────────── #
async def is_admin(chat, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat.id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False


# Enable Welcome
@app.on_message(filters.command(["welcomeon", "welon"]) & filters.group)
async def enable_welcome(client: Client, message: Message):
    if not await is_admin(message.chat, message.from_user.id):
        return await message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    chat_id = message.chat.id
    welc.update_one({"chat_id": chat_id}, {"$set": {"welcome": True}}, upsert=True)
    await message.reply_text("✅ **ᴡᴇʟᴄᴏᴍᴇ sʏsᴛᴇᴍ ᴇɴᴀʙʟᴇᴅ.**")


# Disable Welcome
@app.on_message(filters.command(["welcomeoff", "weloff"]) & filters.group)
async def disable_welcome(client: Client, message: Message):
    if not await is_admin(message.chat, message.from_user.id):
        return await message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    chat_id = message.chat.id
    welc.update_one({"chat_id": chat_id}, {"$set": {"welcome": False}}, upsert=True)
    await message.reply_text("❌ **ᴡᴇʟᴄᴏᴍᴇ sʏsᴛᴇᴍ ᴅɪsᴀʙʟᴇᴅ.**")


# Enable Left
@app.on_message(filters.command(["lefton", "lefon"]) & filters.group)
async def enable_left(client: Client, message: Message):
    if not await is_admin(message.chat, message.from_user.id):
        return await message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    chat_id = message.chat.id
    welc.update_one({"chat_id": chat_id}, {"$set": {"left": True}}, upsert=True)
    await message.reply_text("✅ **ʟᴇғᴛ sʏsᴛᴇᴍ ᴇɴᴀʙʟᴇᴅ.**")


# Disable Left
@app.on_message(filters.command(["leftoff", "lefoff"]) & filters.group)
async def disable_left(client: Client, message: Message):
    if not await is_admin(message.chat, message.from_user.id):
        return await message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
    chat_id = message.chat.id
    welc.update_one({"chat_id": chat_id}, {"$set": {"left": False}}, upsert=True)
    await message.reply_text("❌ **ʟᴇғᴛ sʏsᴛᴇᴍ ᴅɪsᴀʙʟᴇᴅ.**")


# User Joined
@app.on_message(filters.new_chat_members, group=2)
async def welcome_user(client: Client, message: Message):
    chat_id = message.chat.id
    data = welc.find_one({"chat_id": chat_id})
    if not data or not data.get("welcome", False):
        return

    for member in message.new_chat_members:
        user_mention = member.mention
        chat_title = message.chat.title
        msg = random.choice(PURVI_WEL_MSG).format(user=user_mention, chat=chat_title)
        m = await message.reply_text(msg)
        await asyncio.sleep(10)
        await m.delete()


# User Left
@app.on_message(filters.left_chat_member, group=2)
async def goodbye_user(client: Client, message: Message):
    chat_id = message.chat.id
    data = welc.find_one({"chat_id": chat_id})
    if not data or not data.get("left", False):
        return

    user_mention = message.left_chat_member.mention
    chat_title = message.chat.title
    msg = random.choice(PURVI_LEFT_MSG).format(user=user_mention, chat=chat_title)
    m = await message.reply_text(msg)
    await asyncio.sleep(10)
    await m.delete()
