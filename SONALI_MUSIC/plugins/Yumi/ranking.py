from pyrogram import Client, filters, enums
from pymongo import MongoClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
from SONALI_MUSIC import app
from config import MONGO_DB_URI

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["natu_rankings"]
collection = db["ranking"]

user_data = {}
today_stats = {}  # Renamed from 'today' to avoid conflict

MISHI = [
    "https://graph.org/file/f86b71018196c5cfe7344.jpg",
    "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
    "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
    "https://graph.org/file/84de4b440300297a8ecb3.jpg",
    "https://graph.org/file/84e84ff778b045879d24f.jpg",
    "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
    "https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
    "https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
    "https://graph.org/file/37248e7bdff70c662a702.jpg",
    "https://graph.org/file/0bfe29d15e918917d1305.jpg",
]

# ---------------- watcher ---------------- #
@app.on_message(filters.group, group=6)
def today_watcher(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # integer ID
    if chat_id not in today_stats:  # Changed from 'today' to 'today_stats'
        today_stats[chat_id] = {}  # Changed from 'today' to 'today_stats'
    today_stats[chat_id].setdefault(user_id, {"total_messages": 0})  # Changed from 'today' to 'today_stats'
    today_stats[chat_id][user_id]["total_messages"] += 1  # Changed from 'today' to 'today_stats'

@app.on_message(filters.group, group=11)
def _watcher(_, message):
    user_id = message.from_user.id
    user_data.setdefault(user_id, {}).setdefault("total_messages", 0)
    user_data[user_id]["total_messages"] += 1
    collection.update_one({"_id": user_id}, {"$inc": {"total_messages": 1}}, upsert=True)

# ---------------- today leaderboard ---------------- #
@app.on_message(filters.command("today"))
async def today_command(_, message):  # Renamed function from 'today' to 'today_command'
    chat_id = message.chat.id
    if chat_id in today_stats:  # Changed from 'today' to 'today_stats'
        users_data = [(uid, info["total_messages"]) for uid, info in today_stats[chat_id].items()]  # Changed from 'today' to 'today_stats'
        sorted_users = sorted(users_data, key=lambda x: x[1], reverse=True)[:10]

        if sorted_users:
            response = "**✦ 📈 ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
            for idx, (uid, total) in enumerate(sorted_users, start=1):
                try:
                    user = await app.get_users(uid)
                    user_mention = f"[{user.first_name}](tg://user?id={uid})"
                except:
                    user_mention = f"`{uid}`"
                response += f"**{idx}**. {user_mention} ➠ {total}\n"

            button = InlineKeyboardMarkup(
                [[InlineKeyboardButton("ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="overall")]]
            )
            await message.reply_photo(random.choice(MISHI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)  # Fixed parse mode
        else:
            await message.reply_text("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.**")
    else:
        await message.reply_text("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.**")

# ---------------- overall ranking ---------------- #
@app.on_message(filters.command("ranking"))
async def ranking(_, message):
    top_members = collection.find().sort("total_messages", -1).limit(10)

    response = "**✦ 📈 ᴄᴜʀʀᴇɴᴛ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    for idx, member in enumerate(top_members, start=1):
        uid = member["_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total}\n"

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="today")]]
    )
    await message.reply_photo(random.choice(MISHI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)  # Fixed parse mode

# ---------------- callback queries ---------------- #
@app.on_callback_query(filters.regex("today"))
async def today_rank(_, query):
    chat_id = query.message.chat.id
    if chat_id in today_stats:  # Changed from 'today' to 'today_stats'
        users_data = [(uid, info["total_messages"]) for uid, info in today_stats[chat_id].items()]  # Changed from 'today' to 'today_stats'
        sorted_users = sorted(users_data, key=lambda x: x[1], reverse=True)[:10]

        if sorted_users:
            response = "**✦ 📈 ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
            for idx, (uid, total) in enumerate(sorted_users, start=1):
                try:
                    user = await app.get_users(uid)
                    user_mention = f"[{user.first_name}](tg://user?id={uid})"
                except:
                    user_mention = f"`{uid}`"
                response += f"**{idx}**. {user_mention} ➠ {total}\n"

            button = InlineKeyboardMarkup(
                [[InlineKeyboardButton("ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="overall")]]
            )
            await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)  # Fixed parse mode
        else:
            await query.answer("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.**", show_alert=True)
    else:
        await query.answer("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.**", show_alert=True)

@app.on_callback_query(filters.regex("overall"))
async def overall_rank(_, query):
    top_members = collection.find().sort("total_messages", -1).limit(10)

    response = "**✦ 📈 ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    for idx, member in enumerate(top_members, start=1):
        uid = member["_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total}\n"

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="today")]]
    )
    await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)  # Fixed parse mode
