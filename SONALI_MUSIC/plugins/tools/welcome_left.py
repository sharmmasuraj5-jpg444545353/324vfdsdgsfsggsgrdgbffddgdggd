import random
import asyncio
import logging
from SONALI_MUSIC import app
from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient
from config import MONGO_DB_URI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- MongoDB -----------------
try:
    mongo_client = MongoClient(MONGO_DB_URI)
    db = mongo_client["welcome_db"]
    chat_settings = db["chat_settings"]
    mongo_client.admin.command('ping')
    logger.info("MongoDB connection successful")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    chat_settings = None

# ----------------- Globals -----------------
last_welcome = {}
left_message_tasks = {}

ShrutiWelcome = [
    "❖ <b>ʜᴇʏ {user} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!</b>",
    "❖ <b>ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ {user} ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.</b>",
    "❖ <b>ʜᴇʟʟᴏ {user}, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ғᴀᴍɪʟʏ!</b>",
    "❖ <b>ʜᴇʏᴀ {user}, ɢʟᴀᴅ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ ʜᴇʀᴇ!</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ! ʟᴇᴛ's ʜᴀᴠᴇ ғᴜɴ.</b>"
]

ShrutiLeft = [
    "❖ <b>ʙʏᴇ {user} sᴇᴇ ʏᴏᴜ sᴏᴏɴ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ɪᴛ ғᴇᴇʟs ᴇᴍᴘᴛʏ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴜ.</b>",
    "❖ <b>{user} ʜᴀs ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ!</b>",
    "❖ <b>ɢᴏᴏᴅʙʏᴇ {user}, ʜᴏᴘᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ ᴀɢᴀɪɴ sᴏᴏɴ!</b>",
    "❖ <b>{user} ʜᴀs ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴛᴀᴋᴇ ᴄᴀʀᴇ!</b>"
]

# ----------------- Mongo helpers -----------------
def is_welcome_enabled(chat_id):
    if chat_settings is None:
        return True
    try:
        setting = chat_settings.find_one({"chat_id": chat_id})
        return setting.get("welcome", True) if setting else True
    except Exception as e:
        logger.error(f"Error checking welcome status: {e}")
        return True

def is_left_enabled(chat_id):
    if chat_settings is None:
        return True
    try:
        setting = chat_settings.find_one({"chat_id": chat_id})
        return setting.get("left", True) if setting else True
    except Exception as e:
        logger.error(f"Error checking left status: {e}")
        return True

def set_welcome(chat_id, value: bool):
    if chat_settings is None:
        return False
    try:
        chat_settings.update_one({"chat_id": chat_id}, {"$set": {"welcome": value}}, upsert=True)
        return True
    except Exception as e:
        logger.error(f"Error setting welcome status: {e}")
        return False

def set_left(chat_id, value: bool):
    if chat_settings is None:
        return False
    try:
        chat_settings.update_one({"chat_id": chat_id}, {"$set": {"left": value}}, upsert=True)
        return True
    except Exception as e:
        logger.error(f"Error setting left status: {e}")
        return False

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

# ----------------- Welcome/Left helpers -----------------
async def delete_previous_welcome(client, chat_id):
    if chat_id in last_welcome:
        try:
            await client.delete_messages(chat_id, last_welcome[chat_id])
            del last_welcome[chat_id]
        except Exception as e:
            logger.debug(f"Could not delete previous welcome message: {e}")

async def schedule_left_message_deletion(client, chat_id, message_id, delay=30):
    if chat_id in left_message_tasks:
        left_message_tasks[chat_id].cancel()

    async def delete_task():
        try:
            await asyncio.sleep(delay)
            await client.delete_messages(chat_id, message_id)
            if chat_id in left_message_tasks:
                del left_message_tasks[chat_id]
        except asyncio.CancelledError:
            logger.debug(f"Left message deletion task cancelled for chat {chat_id}")
        except Exception as e:
            logger.error(f"Error deleting left message: {e}")

    task = asyncio.create_task(delete_task())
    left_message_tasks[chat_id] = task

# ----------------- Commands -----------------
@app.on_message(filters.command("welcomestatus") & filters.group)
async def welcome_status(client, message: Message):
    try:
        chat_id = message.chat.id
        welcome_status = "ᴇɴᴀʙʟᴇᴅ" if is_welcome_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"
        left_status = "ᴇɴᴀʙʟᴇᴅ" if is_left_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"
        await message.reply_text(
            f"<b>ᴡᴇʟᴄᴏᴍᴇ sᴛᴀᴛᴜs:</b> {welcome_status}\n"
            f"<b>ʟᴇғᴛ sᴛᴀᴛᴜs:</b> {left_status}\n"
            f"<b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat_id}</code>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in welcome_status command: {e}")
        await message.reply_text("❌ <b>An error occurred while fetching status.</b>")

@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(client, message: Message):
    try:
        chat_id = message.chat.id
        chat_title = message.chat.title or "This Group"
        status = "ᴇɴᴀʙʟᴇᴅ" if is_welcome_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data=f"w_on_{chat_id}"),
             InlineKeyboardButton("❌ ᴅɪsᴀʙʟᴇ", callback_data=f"w_off_{chat_id}")]
        ])

        await message.reply_text(
            f"<b>🏷 ɢʀᴏᴜᴘ ɴᴀᴍᴇ:</b> <i>{chat_title}</i>\n"
            f"<b>🆔 ɢʀᴏᴜᴘ ɪᴅ:</b> <code>{chat_id}</code>\n"
            f"<b>📝 ᴡᴇʟᴄᴏᴍᴇ sᴛᴀᴛᴜs:</b> <b>{status}</b>",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in welcome command: {e}")
        await message.reply_text("❌ <b>An error occurred while processing the command.</b>")

@app.on_message(filters.command("left") & filters.group)
async def left_cmd(client, message: Message):
    try:
        chat_id = message.chat.id
        chat_title = message.chat.title or "This Group"
        status = "ᴇɴᴀʙʟᴇᴅ" if is_left_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data=f"l_on_{chat_id}"),
             InlineKeyboardButton("❌ ᴅɪsᴀʙʟᴇ", callback_data=f"l_off_{chat_id}")]
        ])

        await message.reply_text(
            f"<b>🏷 ɢʀᴏᴜᴘ ɴᴀᴍᴇ:</b> <i>{chat_title}</i>\n"
            f"<b>🆔 ɢʀᴏᴜᴘ ɪᴅ:</b> <code>{chat_id}</code>\n"
            f"<b>👋 ʟᴇғᴛ sᴛᴀᴛᴜs:</b> <b>{status}</b>",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in left command: {e}")
        await message.reply_text("❌ <b>An error occurred while processing the command.</b>")

# ----------------- Callback handler -----------------
@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    try:
        user = callback_query.from_user
        data = callback_query.data
        if not data:
            return

        parts = data.split("_")
        if len(parts) < 3:
            return

        action_type, action, chat_id = parts[0], parts[1], int(parts[2])
        if not await is_admin(client, chat_id, user.id):
            await callback_query.answer("⚠️ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!", show_alert=True)
            return

        chat_title = callback_query.message.chat.title or "This Group"
        new_text = ""

        if action_type == "w":
            if action == "on":
                new_text = f"✅ <b>ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>" if set_welcome(chat_id, True) else "❌ <b>Database error.</b>"
            else:
                new_text = f"❌ <b>ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>" if set_welcome(chat_id, False) else "❌ <b>Database error.</b>"
        elif action_type == "l":
            if action == "on":
                new_text = f"✅ <b>ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>" if set_left(chat_id, True) else "❌ <b>Database error.</b>"
            else:
                new_text = f"❌ <b>ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>" if set_left(chat_id, False) else "❌ <b>Database error.</b>"

        if callback_query.message.text != new_text:
            await callback_query.message.edit_text(new_text, parse_mode=enums.ParseMode.HTML)
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Error in callback_toggle: {e}")
        await callback_query.answer("❌ An error occurred!", show_alert=True)

# ----------------- Chat member update -----------------
@app.on_chat_member_updated()
async def handle_chat_member_update(client, chat_member: ChatMemberUpdated):
    try:
        chat_id = chat_member.chat.id
        old_member = getattr(chat_member, 'old_chat_member', None)
        new_member = getattr(chat_member, 'new_chat_member', None)
        user = getattr(new_member, 'user', None) or getattr(old_member, 'user', None)
        if not user or user.is_bot:
            return

        old_status = getattr(old_member, 'status', None)
        new_status = getattr(new_member, 'status', None)

        join_from_statuses = [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED, None]
        join_to_statuses = [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]

        if old_status in join_from_statuses and new_status in join_to_statuses:
            await handle_user_join(client, chat_id, user)
        elif old_status in join_to_statuses and new_status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
            await handle_user_leave(client, chat_id, user)

    except Exception as e:
        logger.error(f"Error in handle_chat_member_update: {e}")

# ----------------- User join/leave handlers -----------------
async def handle_user_join(client, chat_id, user):
    if not is_welcome_enabled(chat_id):
        return
    await delete_previous_welcome(client, chat_id)
    text = random.choice(ShrutiWelcome).format(user=user.mention)
    sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
    last_welcome[chat_id] = sent.id

async def handle_user_leave(client, chat_id, user):
    if not is_left_enabled(chat_id):
        return
    text = random.choice(ShrutiLeft).format(user=user.mention)
    sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
    await schedule_left_message_deletion(client, chat_id, sent.id)

# ----------------- Message-based fallback handlers -----------------
@app.on_message(filters.new_chat_members & filters.group)
async def handle_new_members(client, message: Message):
    chat_id = message.chat.id
    if not is_welcome_enabled(chat_id):
        return
    await delete_previous_welcome(client, chat_id)
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        text = random.choice(ShrutiWelcome).format(user=user.mention)
        sent = await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
        last_welcome[chat_id] = sent.id

@app.on_message(filters.left_chat_member & filters.group)
async def handle_left_member(client, message: Message):
    chat_id = message.chat.id
    user = message.left_chat_member
    if not user or user.is_bot:
        return
    if not is_left_enabled(chat_id):
        return
    text = random.choice(ShrutiLeft).format(user=user.mention)
    sent = await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
    await schedule_left_message_deletion(client, chat_id, sent.id)

logger.info("Welcome/Left module loaded successfully!")
