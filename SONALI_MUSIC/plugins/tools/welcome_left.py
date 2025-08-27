import random
import asyncio
from SONALI_MUSIC import app
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient
from config import MONGO_DB_URI

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["welcome_db"]
chat_settings = db["chat_settings"]

PURVI_WEL_MSG = [
    "❖ ʜᴇʏ {user}, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!",
    "❖ ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ ʜᴇʀᴇ, {user}!",
    "❖ ɢʀᴇᴇᴛɪɴɢs {user}! ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.",
]

PURVI_LEFT_MSG = [
    "❖ ʙʏᴇ ʙʏᴇ {user}! sᴇᴇ ʏᴏᴜ sᴏᴏɴ.",
    "❖ {user} ʟᴇꜰᴛ... ᴛʜᴇ ɢʀᴏᴜᴘ ꜰᴇᴇʟs ᴇᴍᴘᴛʏ.",
    "❖ ɢᴏᴏᴅʙʏᴇ {user}! ᴛᴀᴋᴇ ᴄᴀʀᴇ.",
]

last_welcome = {}

# DB helpers
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

# Admin check
async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")

# Welcome command
@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    status = "✅ Enabled" if is_welcome_enabled(chat_id) else "❌ Disabled"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Enable", callback_data=f"welcome_enable_{chat_id}"),
            InlineKeyboardButton("Disable", callback_data=f"welcome_disable_{chat_id}")
        ]
    ])

    await message.reply_text(
        f"Welcome messages current status in **{chat_title}**: {status}",
        reply_markup=keyboard,
        parse_mode="markdown"
    )

# Left command
@app.on_message(filters.command("left") & filters.group)
async def left_cmd(client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    status = "✅ Enabled" if is_left_enabled(chat_id) else "❌ Disabled"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Enable", callback_data=f"left_enable_{chat_id}"),
            InlineKeyboardButton("Disable", callback_data=f"left_disable_{chat_id}")
        ]
    ])

    await message.reply_text(
        f"Left messages current status in **{chat_title}**: {status}",
        reply_markup=keyboard,
        parse_mode="markdown"
    )

# Callback query handler
@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    data = callback_query.data
    chat_id = int(data.split("_")[-1])
    chat_title = callback_query.message.chat.title

    if not await is_admin(client, chat_id, user.id):
        return await callback_query.answer("This is not for you baby 🥺", show_alert=True)

    new_text = callback_query.message.text

    if "welcome_enable" in data:
        if not is_welcome_enabled(chat_id):
            set_welcome(chat_id, True)
            new_text = f"✅ Welcome messages ENABLED in {chat_title}"
        else:
            new_text = f"⚙ Welcome messages already ENABLED in {chat_title}"

    elif "welcome_disable" in data:
        if is_welcome_enabled(chat_id):
            set_welcome(chat_id, False)
            new_text = f"❌ Welcome messages DISABLED in {chat_title}"
        else:
            new_text = f"⚙ Welcome messages already DISABLED in {chat_title}"

    elif "left_enable" in data:
        if not is_left_enabled(chat_id):
            set_left(chat_id, True)
            new_text = f"✅ Left messages ENABLED in {chat_title}"
        else:
            new_text = f"⚙ Left messages already ENABLED in {chat_title}"

    elif "left_disable" in data:
        if is_left_enabled(chat_id):
            set_left(chat_id, False)
            new_text = f"❌ Left messages DISABLED in {chat_title}"
        else:
            new_text = f"⚙ Left messages already DISABLED in {chat_title}"

    # Edit message and remove buttons
    if callback_query.message.text != new_text:
        await callback_query.message.edit_text(new_text)

# Welcome message handler
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

# Left message handler
@app.on_message(filters.left_chat_member)
async def left(client, message: Message):
    if not is_left_enabled(message.chat.id):
        return

    left_user = message.left_chat_member
    text = random.choice(PURVI_LEFT_MSG).format(user=left_user.mention)
    sent = await message.reply_text(text)

    # Delete after 10 seconds
    await asyncio.sleep(10)
    try:
        await client.delete_messages(message.chat.id, sent.id)
    except:
        pass
