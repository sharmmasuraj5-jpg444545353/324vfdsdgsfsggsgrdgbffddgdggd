import random
import asyncio
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from config import MONGO_DB_URI
from SONALI_MUSIC import app

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["welcome_db"]
chat_settings = db["chat_settings"]

PURVI_WEL_MSG = [
    "❖ ʜᴇʏ {user}, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!",
    "❖ ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ ʜᴇʀᴇ, {user}!",
    "❖ ɢʀᴇᴇᴛɪɴɢs {user}! ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ."
]

PURVI_LEFT_MSG = [
    "❖ ʙʏᴇ ʙʏᴇ {user}! sᴇᴇ ʏᴏᴜ sᴏᴏɴ.",
    "❖ {user} ʟᴇꜰᴛ... ᴛʜᴇ ɢʀᴏᴜᴘ ꜰᴇᴇʟs ᴇᴍᴘᴛʏ.",
    "❖ ɢᴏᴏᴅʙʏᴇ {user}! ᴛᴀᴋᴇ ᴄᴀʀᴇ."
]

last_welcome = {}

# --- DB helpers ---
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

# --- Admin check ---
async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]

# --- /welcome command ---
@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(client, message: Message):
    status = "ENABLED" if is_welcome_enabled(message.chat.id) else "DISABLED"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Enable", callback_data=f"welcome_enable_{message.chat.id}"),
            InlineKeyboardButton("Disable", callback_data=f"welcome_disable_{message.chat.id}")
        ]
    ])
    await message.reply_text(
        f"⚙ Welcome messages current status in {message.chat.title}: {status}",
        reply_markup=keyboard
    )

# --- /left command ---
@app.on_message(filters.command("left") & filters.group)
async def left_cmd(client, message: Message):
    status = "ENABLED" if is_left_enabled(message.chat.id) else "DISABLED"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Enable", callback_data=f"left_enable_{message.chat.id}"),
            InlineKeyboardButton("Disable", callback_data=f"left_disable_{message.chat.id}")
        ]
    ])
    await message.reply_text(
        f"⚙ Left messages current status in {message.chat.title}: {status}",
        reply_markup=keyboard
    )

# --- Callback handler ---
@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    data = callback_query.data
    chat_id = int(data.split("_")[-1])
    chat_title = callback_query.message.chat.title

    if not await is_admin(client, chat_id, user.id):
        return await callback_query.answer("This is not for you baby 🥺", show_alert=True)

    # Welcome toggle
    if "welcome_enable" in data:
        if is_welcome_enabled(chat_id):
            return await callback_query.answer(f"Already enabled in {chat_title}!", show_alert=True)
        set_welcome(chat_id, True)
        await callback_query.answer(f"✅ Welcome enabled in {chat_title}!", show_alert=True)
    
    elif "welcome_disable" in data:
        if not is_welcome_enabled(chat_id):
            return await callback_query.answer(f"Already disabled in {chat_title}!", show_alert=True)
        set_welcome(chat_id, False)
        await callback_query.answer(f"❌ Welcome disabled in {chat_title}!", show_alert=True)

    # Left toggle
    elif "left_enable" in data:
        if is_left_enabled(chat_id):
            return await callback_query.answer(f"Already enabled in {chat_title}!", show_alert=True)
        set_left(chat_id, True)
        await callback_query.answer(f"✅ Left enabled in {chat_title}!", show_alert=True)

    elif "left_disable" in data:
        if not is_left_enabled(chat_id):
            return await callback_query.answer(f"Already disabled in {chat_title}!", show_alert=True)
        set_left(chat_id, False)
        await callback_query.answer(f"❌ Left disabled in {chat_title}!", show_alert=True)

# --- Welcome new members ---
@app.on_message(filters.new_chat_members)
async def welcome(client, message: Message):
    if not is_welcome_enabled(message.chat.id):
        return

    chat_id = message.chat.id
    if chat_id in last_welcome:
        try:
            await client.delete_messages(chat_id, last_welcome[chat_id])
        except:
            pass

    for new_member in message.new_chat_members:
        text = random.choice(PURVI_WEL_MSG).format(user=new_member.mention)
        sent = await message.reply_text(text)
        last_welcome[chat_id] = sent.id

# --- Left member ---
@app.on_message(filters.left_chat_member)
async def left(client, message: Message):
    if not is_left_enabled(message.chat.id):
        return

    left_user = message.left_chat_member
    text = random.choice(PURVI_LEFT_MSG).format(user=left_user.mention)
    sent = await message.reply_text(text)

    await asyncio.sleep(10)
    try:
        await client.delete_messages(message.chat.id, sent.id)
    except:
        pass
