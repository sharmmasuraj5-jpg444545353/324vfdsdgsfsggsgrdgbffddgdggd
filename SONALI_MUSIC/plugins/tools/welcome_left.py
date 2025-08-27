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

# Welcome/Left Messages with HTML formatting
PURVI_WEL_MSG = [
    "❖ <b>Hey {user}</b>, <i>welcome to the group!</i>",
    "❖ <b>Glad to see you {user}</b>! Enjoy your stay.",
    "❖ <b>Greetings {user}</b>! Have fun here.",
]

PURVI_LEFT_MSG = [
    "❖ <b>Bye {user}</b>! See you soon.",
    "❖ <b>{user}</b> left... The group feels empty.",
    "❖ <b>Goodbye {user}</b>! Take care.",
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
        f"<b>Welcome messages current status in {chat_title}:</b> {status}",
        reply_markup=keyboard,
        parse_mode="html"
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
        f"<b>Left messages current status in {chat_title}:</b> {status}",
        reply_markup=keyboard,
        parse_mode="html"
    )

# Callback query handler
@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    data = callback_query.data
    chat_id = int(data.split("_")[-1])
    chat_title = callback_query.message.chat.title

    if not await is_admin(client, chat_id, user.id):
        return await callback_query.answer("This is not for you 🥺", show_alert=True)

    new_text = callback_query.message.text

    if "welcome_enable" in data:
        if not is_welcome_enabled(chat_id):
            set_welcome(chat_id, True)
            new_text = f"✅ <b>Welcome messages ENABLED in {chat_title}</b>"
        else:
            new_text = f"⚙ <b>Welcome messages already ENABLED in {chat_title}</b>"

    elif "welcome_disable" in data:
        if is_welcome_enabled(chat_id):
            set_welcome(chat_id, False)
            new_text = f"❌ <b>Welcome messages DISABLED in {chat_title}</b>"
        else:
            new_text = f"⚙ <b>Welcome messages already DISABLED in {chat_title}</b>"

    elif "left_enable" in data:
        if not is_left_enabled(chat_id):
            set_left(chat_id, True)
            new_text = f"✅ <b>Left messages ENABLED in {chat_title}</b>"
        else:
            new_text = f"⚙ <b>Left messages already ENABLED in {chat_title}</b>"

    elif "left_disable" in data:
        if is_left_enabled(chat_id):
            set_left(chat_id, False)
            new_text = f"❌ <b>Left messages DISABLED in {chat_title}</b>"
        else:
            new_text = f"⚙ <b>Left messages already DISABLED in {chat_title}</b>"

    # Edit message and remove buttons
    if callback_query.message.text != new_text:
        await callback_query.message.edit_text(new_text, parse_mode="html")

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
        sent = await message.reply_text(text, parse_mode="html")
        last_welcome[chat_id] = sent.id

# Left message handler using on_chat_member_updated
from pyrogram.types import ChatMemberUpdated

@app.on_chat_member_updated(filters.group)
async def left_member_handler(client: app, member: ChatMemberUpdated):
    chat_id = member.chat.id
    if not is_left_enabled(chat_id):
        return

    if (
        member.old_chat_member
        and (member.old_chat_member.status in ("member", "administrator", "creator"))
        and (not member.new_chat_member or member.new_chat_member.status in ("left", "kicked"))
    ):
        user = member.old_chat_member.user
        text = random.choice(PURVI_LEFT_MSG).format(user=f"<b>{user.first_name}</b>")
        sent = await client.send_message(chat_id, text, parse_mode="html")

        # Delete after 10 seconds
        await asyncio.sleep(10)
        try:
            await client.delete_messages(chat_id, sent.id)
        except:
            pass
