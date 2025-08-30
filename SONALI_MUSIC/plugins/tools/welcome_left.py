import random
import asyncio
from SONALI_MUSIC import app
from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from pymongo import MongoClient
from config import MONGO_DB_URI

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["welcome_db"]
chat_settings = db["chat_settings"]

PURVI_WEL_MSG = [
    "❖ <b>ʜᴇʏ {user} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!</b>",
    "❖ <b>ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ {user} ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.</b>",
    "❖ <b>ɢʀᴇᴇᴛɪɴɢs {user} ʜᴀᴠᴇ ғᴜɴ ʜᴇʀᴇ.</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ʀᴇᴀᴅʏ ғᴏʀ sᴏᴍᴇ ᴄʜᴀᴛ ᴀɴᴅ ʟᴀᴜɢʜs.</b>",
    "❖ <b>ʜᴇʏ {user} ʏᴏᴜ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʀᴇᴡ!</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ᴄʜᴀᴛ ɪs ʙᴇᴛᴛᴇʀ ᴡɪᴛʜ ʏᴏᴜ.</b>",
    "❖ <b>ɴɪᴄᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ {user} ʜᴏᴘᴇ ʏᴏᴜ ʟɪᴋᴇ ɪᴛ ʜᴇʀᴇ.</b>",
    "❖ <b>ʜᴇʏ {user} ᴘʀᴇᴘᴀʀᴇ ғᴏʀ sᴏᴍᴇ ᴄʜᴀᴛ ᴀɴᴅ ᴍᴇᴍᴇs.</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ᴇᴠᴇʀʏᴏɴᴇ ɪs ʜᴀᴘᴘʏ ʏᴏᴜ'ʀᴇ ʜᴇʀᴇ.</b>",
    "❖ <b>ʜᴇʏ {user} ʟᴇᴛ's sᴛᴀʀᴛ ᴛʜᴇ ғᴜɴ ʙᴀʟʟʀᴏᴏᴍ.</b>",
    "❖ <b>ɢʀᴇᴇᴛɪɴɢs {user} ᴄʜᴀᴛ ɪs ʙᴇᴛᴛᴇʀ ᴡɪᴛʜ ʏᴏᴜ.</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ʀᴇᴀᴅʏ ғᴏʀ sᴏᴍᴇ ᴛᴀʟᴋ ᴀɴᴅ ʟᴀᴜɢʜs.</b>",
    "❖ <b>ʜᴇʏ {user} ʏᴏᴜ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ sǫᴜᴀᴅ.</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ᴛɪᴍᴇ ᴛᴏ ᴄʜᴀᴛ ᴀɴᴅ ᴍᴀᴋᴇ ғʀɪᴇɴᴅs.</b>",
    "❖ <b>ɴɪᴄᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ {user} ʜᴏᴘᴇ ʏᴏᴜ ʟɪᴋᴇ ɪᴛ ʜᴇʀᴇ.</b>",
    "❖ <b>ʜᴇʏ {user} ᴄʜᴀᴛ ɪs ᴊᴜsᴛ ɢᴏᴛ ʙᴇᴛᴛᴇʀ.</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ʀᴇᴀᴅʏ ғᴏʀ sᴏᴍᴇ sᴍɪʟᴇs ᴀɴᴅ ʟᴀᴜɢʜs.</b>",
    "❖ <b>ʜᴇʏ {user} ʟᴇᴛ's ᴄʀᴇᴀᴛᴇ sᴏᴍᴇ ᴍᴇᴍᴏʀɪᴇs ᴛᴏɢᴇᴛʜᴇʀ.</b>",
    "❖ <b>ɢʀᴇᴇᴛɪɴɢs {user} ᴛʜᴇ ᴄʜᴀᴛ ɪs ʙᴜʟʟᴇᴛ ᴡɪᴛʜ ʏᴏᴜ ʜᴇʀᴇ.</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ʀᴇᴀᴅʏ ғᴏʀ ʟᴏᴛs ᴏғ ғᴜɴ ᴀɴᴅ ᴄʜᴀᴛ.</b>",
]

PURVI_LEFT_MSG = [
    "❖ <b>ʙʏᴇ {user} sᴇᴇ ʏᴏᴜ sᴏᴏɴ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ɪᴛ ғᴇᴇʟs ᴇᴍᴘᴛʏ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴜ.</b>",
    "❖ <b>ɢᴏᴏᴅʙʏᴇ {user} ᴛᴀᴋᴇ ᴄᴀʀᴇ.</b>",
    "❖ <b>ғᴀʀᴇᴡᴇʟʟ {user} ᴛʜᴇ ᴄʜᴀᴛ ᴡɪʟʟ ᴍɪss ʏᴏᴜ.</b>",
    "❖ <b>ʙʏᴇ {user} ʀᴇᴍᴇᴍʙᴇʀ ᴛᴏ ᴄᴏᴍᴇ ʙᴀᴄᴋ sᴏᴏɴ.</b>",
    "❖ <b>{user} ʟᴇғᴛ... ᴛʜᴇ ᴍᴇᴍᴏʀɪᴇs ʀᴇᴍᴀɪɴ.</b>",
    "❖ <b>ɢᴏᴏᴅʙʏᴇ {user} ʏᴏᴜ ᴡɪʟʟ ʙᴇ ᴍɪssᴇᴅ.</b>",
    "❖ <b>ʙʏᴇ {user} ᴛʜᴇ ᴄʜᴀᴛ ɪs ɴᴏᴡ ʟᴇss ʙʀɪɢʜᴛ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴜ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ᴛᴀᴋᴇ ᴄᴀʀᴇ!</b>",
    "❖ <b>ғᴀʀᴇᴡᴇʟʟ {user} ᴛʜᴇ ᴅᴀʏ ɪs ʟᴏɴɢᴇʀ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴜ.</b>",
    "❖ <b>ʙʏᴇ {user} ᴛʜᴇ ᴄʜᴀᴛ ɪs ɴᴏᴡ ʟᴇss ᴠɪʙʀᴀɴᴛ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ʀᴇᴍᴇᴍʙᴇʀ ᴛᴏ ᴄʜᴇᴇʀ ᴜᴘ ʟᴀᴛᴇʀ.</b>",
    "❖ <b>ɢᴏᴏᴅʙʏᴇ {user} ʜᴏᴘᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ ᴀɢᴀɪɴ sᴏᴏɴ.</b>",
    "❖ <b>ʙʏᴇ {user} ᴛʜᴇ ᴄʜᴀᴛ ɪs ǫᴜɪᴇᴛ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴜ.</b>",
    "❖ <b>{user} ʟᴇғᴛ... ᴛᴀᴋᴇ ᴄᴀʀᴇ ᴀɴᴅ ᴄʜᴀᴛ sᴏᴏɴ.</b>",
    "❖ <b>ғᴀʀᴇᴡᴇʟʟ {user} ʏᴏᴜ ʟᴇғᴛ ᴀ ᴍᴀʀᴋ ʜᴇʀᴇ.</b>",
    "❖ <b>ʙʏᴇ {user} ᴛʜᴇ ᴄʜᴀᴛ ɪs ɴᴏᴡ ʟᴏɴᴇʟʏ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ᴍɪss ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ.</b>",
    "❖ <b>ɢᴏᴏᴅʙʏᴇ {user} ᴛᴀᴋᴇ ᴄᴀʀᴇ ᴀɴᴅ ᴄᴏᴍᴇ ʙᴀᴄᴋ sᴏᴏɴ.</b>",
    "❖ <b>ʙʏᴇ {user} ᴛʜᴇ ᴄʜᴀᴛ ɪs ɴᴏᴡ ᴍɪssɪɴɢ ʏᴏᴜ.</b>",
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

async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)

@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    status = "ᴇɴᴀʙʟᴇᴅ" if is_welcome_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴇɴᴀʙʟᴇ", callback_data=f"welcome_enable_{chat_id}"),
            InlineKeyboardButton("ᴅɪsᴀʙʟᴇ", callback_data=f"welcome_disable_{chat_id}")
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
            InlineKeyboardButton("ᴇɴᴀʙʟᴇ", callback_data=f"left_enable_{chat_id}"),
            InlineKeyboardButton("ᴅɪsᴀʙʟᴇ", callback_data=f"left_disable_{chat_id}")
        ]
    ])

    await message.reply_text(
    f"<b>⊚ ɢʀᴏᴜᴘ ɴᴀᴍᴇ :-</b> {chat_title}\n"
    f"<b>⋟ ɢʀᴏᴜᴘ ɪᴅ :-</b> {chat_id}\n"
    f"<b>⋟ ʟᴇғᴛ sᴛᴀᴛᴜs :-</b> {status}",
    reply_markup=keyboard,
    parse_mode=enums.ParseMode.HTML
)

@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    data = callback_query.data
    chat_id = int(data.split("_")[-1])
    chat_title = callback_query.message.chat.title

    if not await is_admin(client, chat_id, user.id):
        return await callback_query.answer("ᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ ʙᴀʙʏ 🥺", show_alert=True)

    new_text = callback_query.message.text

    if "welcome_enable" in data:
        if not is_welcome_enabled(chat_id):
            set_welcome(chat_id, True)
            new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
        else:
            new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"

    elif "welcome_disable" in data:
        if is_welcome_enabled(chat_id):
            set_welcome(chat_id, False)
            new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
        else:
            new_text = f"<b>⋟ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"

    elif "left_enable" in data:
        if not is_left_enabled(chat_id):
            set_left(chat_id, True)
            new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
        else:
            new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"

    elif "left_disable" in data:
        if is_left_enabled(chat_id):
            set_left(chat_id, False)
            new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ :- </b>{chat_title}"
        else:
            new_text = f"<b>⋟ ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ :-</b>{chat_title}"

    
    if callback_query.message.text != new_text:
        await callback_query.message.edit_text(new_text, parse_mode=enums.ParseMode.HTML)



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
