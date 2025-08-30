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
    "❖ <b>ɢʀᴇᴇᴛɪɴɢs {user} ʜᴀᴠᴇ ғᴜɴ ʜᴇʀᴇ.</b>",
    # ... बाकी messages
]

PURVI_LEFT_MSG = [
    "❖ <b>ʙʏᴇ {user} sᴇᴇ ʏᴏᴜ sᴏᴏɴ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ɪᴛ ғᴇᴇʟs ᴇᴍᴘᴛʏ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴜ.</b>",
    # ... बाकी messages
]

last_welcome = {}

# Helper functions
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

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "ᴇɴᴀʙʟᴇ",
                callback_data=json.dumps({"action": "welcome_enable", "chat_id": chat_id})
            ),
            InlineKeyboardButton(
                "ᴅɪsᴀʙʟᴇ",
                callback_data=json.dumps({"action": "welcome_disable", "chat_id": chat_id})
            )
        ]
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

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "ᴇɴᴀʙʟᴇ",
                callback_data=json.dumps({"action": "left_enable", "chat_id": chat_id})
            ),
            InlineKeyboardButton(
                "ᴅɪsᴀʙʟᴇ",
                callback_data=json.dumps({"action": "left_disable", "chat_id": chat_id})
            )
        ]
    ])

    await message.reply_text(
        f"<b>⊚ ɢʀᴏᴜᴘ ɴᴀᴍᴇ :-</b> {chat_title}\n"
        f"<b>⋟ ɢʀᴏᴜᴘ ɪᴅ :-</b> {chat_id}\n"
        f"<b>⋟ ʟᴇғᴛ sᴛᴀᴛᴜs :-</b> {status}",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

# Callback query handler
@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    try:
        data = json.loads(callback_query.data)
        action = data.get("action")
        chat_id = data.get("chat_id")
    except Exception:
        return await callback_query.answer("ᴄᴀɴ'ᴛ ʀᴇᴀᴅ ᴅᴀᴛᴀ ❌", show_alert=True)

    if not await is_admin(client, chat_id, user.id):
        return await callback_query.answer("ᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ 🥺", show_alert=True)

    chat_title = callback_query.message.chat.title
    new_text = ""

    if action == "welcome_enable":
        set_welcome(chat_id, True)
        new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
    elif action == "welcome_disable":
        set_welcome(chat_id, False)
        new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
    elif action == "left_enable":
        set_left(chat_id, True)
        new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
    elif action == "left_disable":
        set_left(chat_id, False)
        new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"

    await callback_query.message.edit_text(new_text, parse_mode=enums.ParseMode.HTML)

# Welcome new member
@app.on_chat_member_updated()
async def welcome(client, chat_member: ChatMemberUpdated):
    chat_id = chat_member.chat.id
    user = chat_member.new_chat_member.user

    if chat_member.old_chat_member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.KICKED] and \
       chat_member.new_chat_member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.RESTRICTED]:

        if not is_welcome_enabled(chat_id):
            return

        if chat_id in last_welcome:
            try:
                await client.delete_messages(chat_id, last_welcome[chat_id])
            except:
                pass

        text = random.choice(PURVI_WEL_MSG).format(user=user.mention)
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
        last_welcome[chat_id] = sent.id

# Left member handler
@app.on_chat_member_updated(filters.group)
async def left_member_handler(client: app, member: ChatMemberUpdated):
    chat_id = member.chat.id
    if not is_left_enabled(chat_id):
        return

    if (
        member.old_chat_member
        and (member.old_chat_member.status in (enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER))
        and (member.new_chat_member is None or member.new_chat_member.status in (enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED))
    ):
        user = member.old_chat_member.user
        text = random.choice(PURVI_LEFT_MSG).format(user=f"<b>{user.first_name}</b>")
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)

        await asyncio.sleep(30)
        try:
            await client.delete_messages(chat_id, sent.id)
        except:
            pass
