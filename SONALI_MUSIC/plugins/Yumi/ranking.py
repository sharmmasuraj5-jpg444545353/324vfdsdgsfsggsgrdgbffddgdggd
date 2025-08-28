from pyrogram import Client, filters, enums
from pymongo import MongoClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import time
from datetime import datetime, timedelta
from SONALI_MUSIC import app
from config import MONGO_DB_URI
import asyncio

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["purvi_rankings"]
collection = db["ranking"]
weekly_collection = db["weekly_ranking"]
today_collection = db["today_ranking"]

user_data = {}
today_stats = {}
weekly_stats = {}

PURVI = [
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

# Bot mention format
def get_bot_mention():
    return f"[{app.me.first_name}](tg://user?id={app.me.id})"

# Daily data reset function
def reset_daily_data():
    global today_stats
    today_stats = {}
    today_collection.delete_many({})
    print("Daily data has been reset!")

# Reset daily data every day at midnight
async def daily_reset_scheduler():
    while True:
        now = datetime.now()
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        wait_seconds = (next_midnight - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        reset_daily_data()

# Weekly data reset function
def reset_weekly_data():
    global weekly_stats
    weekly_stats = {}
    weekly_collection.delete_many({})
    print("Weekly data has been reset!")

# Reset weekly data every Sunday
async def weekly_reset_scheduler():
    while True:
        now = datetime.now()
        next_sunday = now + timedelta(days=(6 - now.weekday() + 7) % 7)
        next_sunday = next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        wait_seconds = (next_sunday - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        reset_weekly_data()

# ---------------- watcher ---------------- #
@app.on_message(filters.group, group=6)
async def today_watcher(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id not in today_stats:
        today_stats[chat_id] = {}
    today_stats[chat_id].setdefault(user_id, {"total_messages": 0})
    today_stats[chat_id][user_id]["total_messages"] += 1
    
    today_collection.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"total_messages": 1}},
        upsert=True
    )

@app.on_message(filters.group, group=11)
async def _watcher(_, message):
    user_id = message.from_user.id
    
    user_data.setdefault(user_id, {}).setdefault("total_messages", 0)
    user_data[user_id]["total_messages"] += 1
    
    collection.update_one({"_id": user_id}, {"$inc": {"total_messages": 1}}, upsert=True)
    weekly_collection.update_one({"_id": user_id}, {"$inc": {"total_messages": 1}}, upsert=True)
    
    if user_id not in weekly_stats:
        weekly_stats[user_id] = 0
    weekly_stats[user_id] += 1

# ---------------- Main Leaderboard Panel ---------------- #
@app.on_message(filters.command(["ranking", "leaderboard", "rank"]))
async def leaderboard_panel(_, message):
    group_name = message.chat.title
    bot_mention = get_bot_mention()
    caption = f"""
**✦ 🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴘᴀɴᴇʟ ✦**

**ɢʀᴏᴜᴘ:** {group_name}

**ᴄʜᴇᴄᴋ ɢʀᴏᴜᴘ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ʙʏ ᴛᴀᴘᴘɪɴɢ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ↓**

**ʙʏ :- {bot_mention}**
    """

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="rank_show_leaderboard_buttons")]
    ])

    await message.reply_photo(
        random.choice(PURVI),
        caption=caption,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.MARKDOWN
    )

# ---------------- today leaderboard ---------------- #
@app.on_message(filters.command("today"))
async def today_command(_, message):
    chat_id = message.chat.id
    
    today_members = today_collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

    response = "**✦ 📈 ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    count = 0
    
    for idx, member in enumerate(today_members, start=1):
        uid = member["user_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total} messages\n"
        count += 1

    if count > 0:
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.me.username}?startgroup=true")]
        ])
        await message.reply_photo(random.choice(PURVI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await message.reply_text("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.**")

# ---------------- weekly ranking ---------------- #
@app.on_message(filters.command("weekly"))
async def weekly_command(_, message):
    top_members = weekly_collection.find().sort("total_messages", -1).limit(10)

    response = "**✦ 📈 ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    for idx, member in enumerate(top_members, start=1):
        uid = member["_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total} messages\n"

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.me.username}?startgroup=true")]
    ])
    await message.reply_photo(random.choice(PURVI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)

# ---------------- overall ranking ---------------- #
@app.on_message(filters.command("overall"))
async def overall_command(_, message):
    top_members = collection.find().sort("total_messages", -1).limit(10)

    response = "**✦ 🏅 ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    for idx, member in enumerate(top_members, start=1):
        uid = member["_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total} messages\n"

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.me.username}?startgroup=true")]
    ])
    await message.reply_photo(random.choice(PURVI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)

# ---------------- Show Leaderboard Buttons ---------------- #
@app.on_callback_query(filters.regex("^rank_show_leaderboard_buttons$"))
async def show_leaderboard_buttons(_, query):
    group_name = query.message.chat.title
    bot_mention = get_bot_mention()
    caption = f"""
**✦ 🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴘᴀɴᴇʟ ✦**

**ɢʀᴏᴜᴘ:** {group_name}

**ᴄʜᴏᴏsᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴛʏᴘᴇ ↓**

**ʙʏ :- {bot_mention}**
    """

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_panel_today"),
         InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_panel_weekly")],
        [InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_panel_overall")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="rank_back_to_panel")]
    ])

    await query.message.edit_text(caption, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)

# ---------------- callback queries for panel ---------------- #
@app.on_callback_query(filters.regex("^rank_panel_"))
async def panel_callback_handler(_, query):
    data = query.data
    
    if data == "rank_panel_today":
        await show_today_leaderboard(query)
    elif data == "rank_panel_weekly":
        await show_weekly_leaderboard(query)
    elif data == "rank_panel_overall":
        await show_overall_leaderboard(query)

async def show_today_leaderboard(query):
    chat_id = query.message.chat.id
    
    today_members = today_collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

    response = "**✦ 📊 ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    count = 0
    
    for idx, member in enumerate(today_members, start=1):
        uid = member["user_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total} messages\n"
        count += 1

    if count > 0:
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_weekly"),
             InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_overall")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴘᴀɴᴇʟ", callback_data="rank_back_to_panel")]
        ])
        await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await query.answer("❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.", show_alert=True)

async def show_weekly_leaderboard(query):
    top_members = weekly_collection.find().sort("total_messages", -1).limit(10)

    response = "**✦ 📈 ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    for idx, member in enumerate(top_members, start=1):
        uid = member["_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total} messages\n"

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_today"),
         InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_overall")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴘᴀɴᴇʟ", callback_data="rank_back_to_panel")]
    ])
    await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)

async def show_overall_leaderboard(query):
    top_members = collection.find().sort("total_messages", -1).limit(10)

    response = "**✦ 🏅 ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    for idx, member in enumerate(top_members, start=1):
        uid = member["_id"]
        total = member["total_messages"]
        try:
            user = await app.get_users(uid)
            user_mention = f"[{user.first_name}](tg://user?id={uid})"
        except:
            user_mention = f"`{uid}`"
        response += f"**{idx}**. {user_mention} ➠ {total} messages\n"

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_today"),
         InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_weekly")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴘᴀɴᴇʟ", callback_data="rank_back_to_panel")]
    ])
    await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)

# ---------------- regular callback queries ---------------- #
@app.on_callback_query(filters.regex("^rank_(today|weekly|overall|back_to_panel)$"))
async def regular_callback_handler(_, query):
    data = query.data.replace("rank_", "")
    
    if data == "today":
        await show_today_leaderboard(query)
    elif data == "weekly":
        await show_weekly_leaderboard(query)
    elif data == "overall":
        await show_overall_leaderboard(query)
    elif data == "back_to_panel":
        group_name = query.message.chat.title
        bot_mention = get_bot_mention()
        caption = f"""
**✦ 🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴘᴀɴᴇʟ ✦**

**ɢʀᴏᴜᴘ:** {group_name}

**ᴄʜᴏᴏsᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴛʏᴘᴇ ↓**

**ʙʏ :- {bot_mention}**
        """

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_panel_today"),
             InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_panel_weekly")],
            [InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_panel_overall")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="rank_back_to_main")]
        ])

        await query.message.edit_text(caption, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)

# ---------------- Back to Main ---------------- #
@app.on_callback_query(filters.regex("^rank_back_to_main$"))
async def back_to_main_handler(_, query):
    group_name = query.message.chat.title
    bot_mention = get_bot_mention()
    caption = f"""
**✦ 🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴘᴀɴᴇʟ ✦**

**ɢʀᴏᴜᴘ:** {group_name}

**ᴄʜᴇᴄᴋ ɢʀᴏᴜᴘ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ʙʏ ᴛᴀᴘᴘɪɴɢ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ↓**

**ʙʏ :- {bot_mention}**
    """

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="rank_show_leaderboard_buttons")]
    ])

    await query.message.edit_text(caption, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)

# Start schedulers
asyncio.create_task(daily_reset_scheduler())
asyncio.create_task(weekly_reset_scheduler())
