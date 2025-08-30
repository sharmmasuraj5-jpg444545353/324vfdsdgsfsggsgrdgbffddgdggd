import random
import asyncio
import json
from SONALI_MUSIC import app
from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from pymongo import MongoClient
from config import MONGO_DB_URI

# MongoDB setup
mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["welcome_db"]
chat_settings = db["chat_settings"]

# Welcome & Left messages
PURVI_WEL_MSG = [
    "❖ <b>ʜᴇʏ {user} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!</b>",
    "❖ <b>ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ {user} ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.</b>",
    # ... बाकी messages
]

PURVI_LEFT_MSG = [
    "❖ <b>ʙʏᴇ {user} sᴇᴇ ʏᴏᴜ sᴏᴏɴ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ɪᴛ ғᴇᴇʟs ᴇᴍᴘᴛʏ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴢ.</b>",
    # ... बाकी messages
]

last_welcome = {}

# Helpers
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

async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)

# Commands
@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    status = "ᴇɴᴀʙʟᴇᴅ" if is_welcome_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

    # Use shorter callback data to avoid BUTTON_DATA_INVALID error
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴇɴᴀʙʟᴇ", callback_data=f"wel_en_{chat_id}"),
         InlineKeyboardButton("ᴅɪsᴀʙʟᴇ", callback_data=f"wel_dis_{chat_id}")]
    ])

    await message.reply_text(
        f"<b>⊚ ɢʀᴏᴜᴘ ɴᴀᴍᴇ :-</b> {chat_title}\n"
        f"<b>⋟ ɢʀᴏᴜᴘ ɪᴅ :-</b> {chat_id}\n"
        f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ sᴛᴀᴛᴜs :-</b> {status}",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.command("left") & filters.group)
async def left_cmd(client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    status = "ᴇɴᴀʙʟᴇᴅ" if is_left_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

    # Use shorter callback data to avoid BUTTON_DATA_INVALID error
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴇɴᴀʙʟᴇ", callback_data=f"left_en_{chat_id}"),
         InlineKeyboardButton("ᴅɪsᴀʙʟᴇ", callback_data=f"left_dis_{chat_id}")]
    ])

    await message.reply_text(
        f"<b>⊚ ɢʀᴏᴜᴘ ɴᴀᴍᴇ :-</b> {chat_title}\n"
        f"<b>⋟ ɢʀᴏᴜᴘ ɪᴅ :-</b> {chat_id}\n"
        f"<b>⋟ ʟᴇғᴛ sᴛᴀᴛᴜs :-</b> {status}",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

# Callback handler
@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    data = callback_query.data
    
    if not data:
        return
    
    # Parse the simplified callback data
    if data.startswith("wel_en_"):
        chat_id = int(data[7:])
        action = "enable"
        type_ = "welcome"
    elif data.startswith("wel_dis_"):
        chat_id = int(data[8:])
        action = "disable"
        type_ = "welcome"
    elif data.startswith("left_en_"):
        chat_id = int(data[8:])
        action = "enable"
        type_ = "left"
    elif data.startswith("left_dis_"):
        chat_id = int(data[9:])
        action = "disable"
        type_ = "left"
    else:
        return

    if not await is_admin(client, chat_id, user.id):
        return await callback_query.answer("ᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ 🥺", show_alert=True)

    chat_title = callback_query.message.chat.title
    new_text = ""

    if type_ == "welcome":
        if action == "enable":
            if not is_welcome_enabled(chat_id):
                set_welcome(chat_id, True)
                new_text = f"<b>⋟ ᴡᴇʟᴏᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
            else:
                new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
        elif action == "disable":
            if is_welcome_enabled(chat_id):
                set_welcome(chat_id, False)
                new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
            else:
                new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"

    elif type_ == "left":
        if action == "enable":
            if not is_left_enabled(chat_id):
                set_left(chat_id, True)
                new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
            else:
                new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
        elif action == "disable":
            if is_left_enabled(chat_id):
                set_left(chat_id, False)
                new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
            else:
                new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ :-</b>{chat_title}"

    if new_text and callback_query.message.text != new_text:
        await callback_query.message.edit_text(new_text, parse_mode=enums.ParseMode.HTML)
    
    await callback_query.answer()

# Welcome handler - FIXED
@app.on_chat_member_updated()
async def welcome(client, chat_member: ChatMemberUpdated):
    chat_id = chat_member.chat.id
    
    # Check if this is a join event
    if (chat_member.old_chat_member is None or 
        chat_member.old_chat_member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]) and \
        chat_member.new_chat_member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        
        if not is_welcome_enabled(chat_id):
            return

        user = chat_member.new_chat_member.user
        
        # Delete previous welcome message if exists
        if chat_id in last_welcome:
            try:
                await client.delete_messages(chat_id, last_welcome[chat_id])
            except:
                pass

        text = random.choice(PURVI_WEL_MSG).format(user=user.mention)
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
        last_welcome[chat_id] = sent.id

# Left handler - FIXED
@app.on_chat_member_updated()
async def left_member_handler(client: app, member: ChatMemberUpdated):
    chat_id = member.chat.id
    
    # Check if this is a leave event
    if (member.old_chat_member is not None and 
        member.old_chat_member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]) and \
        (member.new_chat_member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]):
        
        if not is_left_enabled(chat_id):
            return

        user = member.old_chat_member.user
        text = random.choice(PURVI_LEFT_MSG).format(user=f"<b>{user.first_name}</b>")
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)

        # Auto-delete after 30 seconds
        await asyncio.sleep(30)
        try:
            await client.delete_messages(chat_id, sent.id)
        except:
            pass
