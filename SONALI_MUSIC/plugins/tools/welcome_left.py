import random
import asyncio
from pyrogram import filters, enums
from pyrogram.types import Message, ChatMemberUpdated
from pymongo import MongoClient
from SONALI_MUSIC import app
from config import MONGO_DB_URI

# ---------------- MongoDB ----------------
mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["welcome_db"]
chat_settings = db["chat_settings"]

# ---------------- Globals ----------------
last_welcome = {}
last_left = {}
left_tasks = {}

ShrutiWelcome = [
    "❖ <b>ʜᴇʏ {user} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!</b>",
    "❖ <b>ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ {user} ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.</b>",
]

ShrutiLeft = [
    "❖ <b>ʙʏᴇ {user} sᴇᴇ ʏᴏᴜ sᴏᴏɴ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ.</b>",
]

# ---------------- Mongo helpers ----------------
def is_welcome_enabled(chat_id):
    setting = chat_settings.find_one({"chat_id": chat_id})
    return setting.get("welcome", True) if setting else True

def is_left_enabled(chat_id):
    setting = chat_settings.find_one({"chat_id": chat_id})
    return setting.get("left", True) if setting else True

# ---------------- Helpers ----------------
async def delete_previous_left(chat_id, client):
    if chat_id in last_left:
        try:
            await client.delete_messages(chat_id, last_left[chat_id])
        except:
            pass

async def schedule_left_delete(chat_id, message_id, client, delay=30):
    if chat_id in left_tasks:
        left_tasks[chat_id].cancel()
    async def task():
        await asyncio.sleep(delay)
        try:
            await client.delete_messages(chat_id, message_id)
        except:
            pass
    left_tasks[chat_id] = asyncio.create_task(task())

# ---------------- Welcome ----------------
@app.on_message(filters.new_chat_members & filters.group)
async def welcome_members(client, message: Message):
    chat_id = message.chat.id
    if not is_welcome_enabled(chat_id):
        return
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        text = random.choice(ShrutiWelcome).format(user=user.mention)
        sent = await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
        last_welcome[chat_id] = sent.id

# ---------------- Left ----------------
@app.on_message(filters.left_chat_member & filters.group)
async def left_members_message(client, message: Message):
    chat_id = message.chat.id
    user = message.left_chat_member
    if not user or user.is_bot or not is_left_enabled(chat_id):
        return
    await delete_previous_left(chat_id, client)
    text = random.choice(ShrutiLeft).format(user=user.mention)
    sent = await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
    last_left[chat_id] = sent.id
    await schedule_left_delete(chat_id, sent.id, client)

# ---------------- ChatMemberUpdated fallback ----------------
@app.on_chat_member_updated()
async def handle_member_update(client, update: ChatMemberUpdated):
    chat_id = update.chat.id
    old_status = update.old_chat_member.status if update.old_chat_member else None
    new_status = update.new_chat_member.status if update.new_chat_member else None
    user = update.new_chat_member.user if update.new_chat_member else update.old_chat_member.user
    if not user or user.is_bot:
        return

    # Join
    join_from = [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED, None]
    join_to = [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    if old_status in join_from and new_status in join_to and is_welcome_enabled(chat_id):
        text = random.choice(ShrutiWelcome).format(user=user.mention)
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
        last_welcome[chat_id] = sent.id

    # Left
    leave_from = [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    leave_to = [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]
    if old_status in leave_from and new_status in leave_to and is_left_enabled(chat_id):
        await delete_previous_left(chat_id, client)
        text = random.choice(ShrutiLeft).format(user=user.mention)
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
        last_left[chat_id] = sent.id
        await schedule_left_delete(chat_id, sent.id, client)

print("✅ Welcome/Left module loaded successfully!")
