from pyrogram import Client, filters, enums
from pymongo import MongoClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import time
from datetime import datetime, timedelta
from SONALI_MUSIC import app
import asyncio
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, PeerIdInvalid

mongo_client = MongoClient("mongodb+srv://Rishant:Thakur@cluster0.g5kjakc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["purvi_rankings"]
collection = db["ranking"]
weekly_collection = db["weekly_ranking"]
today_collection = db["today_ranking"]
meta_collection = db["meta"]

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


def get_bot_mention():
    return f"[{app.me.first_name}](tg://user?id={app.me.id})"


def reset_daily_data():
    global today_stats
    today_stats = {}
    today_collection.delete_many({})
    print("ᴅᴀɪʟʏ ᴅᴀᴛᴀ ʜᴀs ʙᴇᴇɴ ʀᴇsᴇᴛ!")


async def daily_reset_scheduler():
    while True:
        try:
            now = datetime.now()
            # ᴄᴀʟᴄᴜʟᴀᴛᴇ ɴᴇxᴛ ᴍɪᴅɴɪɢʜᴛ
            next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            wait_seconds = (next_midnight - now).total_seconds()
            print(f"ᴅᴀɪʟʏ ʀᴇsᴇᴛ sᴄʜᴇᴅᴜʟᴇᴅ ɪɴ {wait_seconds} sᴇᴄᴏɴᴅs")
            await asyncio.sleep(wait_seconds)
            reset_daily_data()
        except Exception as e:
            print(f"ᴇʀʀᴏʀ ɪɴ ᴅᴀɪʟʏ ʀᴇsᴇᴛ sᴄʜᴇᴅᴜʟᴇʀ: {e}")
            await asyncio.sleep(3600)


def reset_weekly_data():
    global weekly_stats
    weekly_stats = {}
    weekly_collection.delete_many({})
    meta_collection.update_one(
        {"_id": "weekly_reset"},
        {"$set": {"last_reset": datetime.utcnow()}},
        upsert=True
    )
    print("✅ ᴡᴇᴇᴋʟʏ ᴅᴀᴛᴀ ʜᴀs ʙᴇᴇɴ ʀᴇsᴇᴛ!")


async def weekly_reset_scheduler():
    while True:
        try:
            record = meta_collection.find_one({"_id": "weekly_reset"})
            last_reset = record["last_reset"] if record else None

            if not last_reset:
                reset_weekly_data()
                last_reset = datetime.utcnow()

            next_reset = last_reset + timedelta(days=7)
            now = datetime.utcnow()

            if now >= next_reset:
                reset_weekly_data()
                next_reset = datetime.utcnow() + timedelta(days=7)

            wait_seconds = (next_reset - now).total_seconds()
            print(f"⏳ ɴᴇxᴛ ᴡᴇᴇᴋʟʏ ʀᴇsᴇᴛ sᴄʜᴇᴅᴜʟᴇᴅ ɪɴ {wait_seconds} sᴇᴄᴏɴᴅs")
            await asyncio.sleep(wait_seconds)

        except Exception as e:
            print(f"⚠️ ᴇᴛʀᴏʀ ɪɴ ᴡᴇᴇᴋʟʏ ʀᴇsᴇᴛ sᴄʜᴇᴅᴜʟᴇʀ :- {e}")
            await asyncio.sleep(3600)


@app.on_message(filters.group, group=6)
async def today_watcher(_, message):
    try:
        if not message.from_user:
            return
        
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
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ᴛᴏᴅᴀʏ_ᴡᴀᴛᴄʜᴇʀ: {e}")


@app.on_message(filters.group, group=11)
async def _watcher(_, message):
    try:
        # ᴄʜᴇᴄᴋ ɪғ ᴍᴇssᴀɢᴇ ʜᴀs ᴀ ᴜsᴇʀ
        if not message.from_user:
            return
        
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # ᴜᴘᴅᴀᴛᴇ ᴏᴠᴇʀᴀʟʟ ʀᴀɴᴋɪɴɢ ᴡɪᴛʜ ᴄʜᴀᴛ_ɪᴅ
        collection.update_one(
            {"chat_id": chat_id, "user_id": user_id}, 
            {"$inc": {"total_messages": 1}}, 
            upsert=True
        )
        
        # ᴜᴘᴅᴀᴛᴇ ᴡᴇᴇᴋʟʏ ʀᴀɴᴋɪɴɢ ᴡɪᴛʜ ᴄʜᴀᴛ_ɪᴅ
        weekly_collection.update_one(
            {"chat_id": chat_id, "user_id": user_id}, 
            {"$inc": {"total_messages": 1}}, 
            upsert=True
        )
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ _ᴡᴀᴛᴄʜᴇʀ: {e}")


@app.on_message(filters.command(["ranking", "leaderboard", "rank"]))
async def leaderboard_panel(_, message):
    try:
        group_name = message.chat.title
        bot_mention = get_bot_mention()
        caption = f"""
**✦ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴘᴀɴɴᴇʟ 🏆**

**⊚ ɢʀᴏᴜᴘ ➠** {group_name}

**⊚ ᴄʜᴇᴄᴋ ɢʀᴏᴜᴘ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ʙʏ ᴛᴀᴘ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ↓**

**➻ ʙʏ ➠ {bot_mention}**
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
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ_ᴘᴀɴᴇʟ: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴅɪsᴘʟᴀʏɪɴɢ ᴛʜᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴘᴀɴᴇʟ.")


@app.on_message(filters.command("today"))
async def today_command(_, message):
    try:
        chat_id = message.chat.id
        
        today_members = today_collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

        response = "**✦ ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ 📈**\n\n"
        count = 0
        
        for idx, member in enumerate(today_members, start=1):
            uid = member["user_id"]
            total = member["total_messages"]
            try:
                user = await app.get_users(uid)
                user_mention = f"[{user.first_name}](tg://user?id={uid})"
            except (PeerIdInvalid, UserNotParticipant):
                user_mention = f"`{uid}`"
            except Exception:
                user_mention = f"`{uid}`"
                
            response += f"**{idx}**. {user_mention} ➠ {total} ᴍsɢ\n"
            count += 1

        if count > 0:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.me.username}?startgroup=true")]
            ])
            await message.reply_photo(random.choice(PURVI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await message.reply_text("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.**")
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ᴛᴏᴅᴀʏ_ᴄᴏᴍᴍᴀɴᴅ: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ᴛᴏᴅᴀʏ's ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.")


@app.on_message(filters.command("weekly"))
async def weekly_command(_, message):
    try:
        chat_id = message.chat.id
        
        # ғɪʟᴛᴇʀ ʙʏ ᴄʜᴀᴛ_ɪᴅ ғᴏʀ ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ
        top_members = weekly_collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

        response = "**✦ ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ 📈**\n\n"
        count = 0
        for idx, member in enumerate(top_members, start=1):
            uid = member["user_id"]
            total = member["total_messages"]
            try:
                user = await app.get_users(uid)
                user_mention = f"[{user.first_name}](tg://user?id={uid})"
            except (PeerIdInvalid, UserNotParticipant):
                user_mention = f"`{uid}`"
            except Exception:
                user_mention = f"`{uid}`"
                
            response += f"**{idx}**. {user_mention} ➠ {total} ᴍsɢ\n"
            count += 1

        if count > 0:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.me.username}?startgroup=true")]
            ])
            await message.reply_photo(random.choice(PURVI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await message.reply_text("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴡᴇᴇᴋʟʏ.**")
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ᴡᴇᴇᴋʟʏ_ᴄᴏᴍᴍᴀɴᴅ: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʟʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.")


@app.on_message(filters.command("overall"))
async def overall_command(_, message):
    try:
        chat_id = message.chat.id
        
        # ғɪʟᴛᴇʀ ʙʏ ᴄʜᴀᴛ_ɪᴅ ғᴏʀ ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ
        top_members = collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

        response = "**✦ ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ 🏅**\n\n"
        count = 0
        for idx, member in enumerate(top_members, start=1):
            uid = member["user_id"]
            total = member["total_messages"]
            try:
                user = await app.get_users(uid)
                user_mention = f"[{user.first_name}](tg://user?id={uid})"
            except (PeerIdInvalid, UserNotParticipant):
                user_mention = f"`{uid}`"
            except Exception:
                user_mention = f"`{uid}`"
                
            response += f"**{idx}**. {user_mention} ➠ {total} ᴍsɢ\n"
            count += 1

        if count > 0:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙", url=f"https://t.me/{app.me.username}?startgroup=true")]
            ])
            await message.reply_photo(random.choice(PURVI), caption=response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await message.reply_text("**❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴏᴠᴇʀᴀʟʟ.**")
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ᴏᴠᴇʀᴀʟʟ_ᴄᴏᴍᴍᴀɴᴅ: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.")


# ᴄᴀʟʟʙᴀᴄᴋ ǫᴜᴇʀʏ ʜᴀɴᴅʟᴇʀs
@app.on_callback_query(filters.regex("^rank_show_leaderboard_buttons$"))
async def show_leaderboard_buttons(_, query):
    try:
        group_name = query.message.chat.title
        bot_mention = get_bot_mention()
        caption = f"""
**✦ ᴄʜᴏᴏsᴇ ᴀ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴛʏᴘᴇ 🏅**

**⊚ ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴄʜᴇᴄᴋ ʙʏ ➠**

`/today` ➠ ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.
`/weekly` ➠ ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.
`/overall` ➠ ᴀʟʟ ᴛɪᴍᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.

**➻ ʙʏ ➠ {bot_mention}**
        """

        buttons = InlineKeyboardMarkup([
            [
             InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_panel_today"),
             InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_panel_weekly")
            ],
            
            [
             InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_panel_overall"),
             InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="rank_back_to_main")
            ]
        ])

        await query.message.edit_text(caption, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ sʜᴏᴡ_ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ_ʙᴜᴛᴛᴏɴs: {e}")
        await query.answer("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.", show_alert=True)


@app.on_callback_query(filters.regex("^rank_panel_"))
async def panel_callback_handler(_, query):
    try:
        data = query.data
        
        if data == "rank_panel_today":
            await show_today_leaderboard(query)
        elif data == "rank_panel_weekly":
            await show_weekly_leaderboard(query)
        elif data == "rank_panel_overall":
            await show_overall_leaderboard(query)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ᴘᴀɴᴇʟ_ᴄᴀʟʟʙᴀᴄᴋ_ʜᴀɴᴅʟᴇʀ: {e}")
        await query.answer("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.", show_alert=True)


async def show_today_leaderboard(query):
    try:
        chat_id = query.message.chat.id
        
        today_members = today_collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

        response = "**✦ ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ 📊**\n\n"
        count = 0
        
        for idx, member in enumerate(today_members, start=1):
            uid = member["user_id"]
            total = member["total_messages"]
            try:
                user = await app.get_users(uid)
                user_mention = f"[{user.first_name}](tg://user?id={uid})"
            except (PeerIdInvalid, UserNotParticipant):
                user_mention = f"`{uid}`"
            except Exception:
                user_mention = f"`{uid}`"
                
            response += f"**{idx}**. {user_mention} ➠ {total} ᴍsɢ\n"
            count += 1

        if count > 0:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_weekly"),
                 InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_overall")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="rank_back_to_panel")]
            ])
            await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await query.answer("❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.", show_alert=True)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ sʜᴏᴡ_ᴛᴏᴅᴀʏ_ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ: {e}")
        await query.answer("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.", show_alert=True)


async def show_weekly_leaderboard(query):
    try:
        chat_id = query.message.chat.id
        
        # ғɪʟᴛᴇʀ ʙʏ ᴄʜᴀᴛ_ɪᴅ ғᴏʀ ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ
        top_members = weekly_collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

        response = "**✦ ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ 📈**\n\n"
        count = 0
        for idx, member in enumerate(top_members, start=1):
            uid = member["user_id"]
            total = member["total_messages"]
            try:
                user = await app.get_users(uid)
                user_mention = f"[{user.first_name}](tg://user?id={uid})"
            except (PeerIdInvalid, UserNotParticipant):
                user_mention = f"`{uid}`"
            except Exception:
                user_mention = f"`{uid}`"
                
            response += f"**{idx}**. {user_mention} ➠ {total} ᴍsɢ\n"
            count += 1

        if count > 0:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_today"),
                 InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_overall")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="rank_back_to_panel")]
            ])
            await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await query.answer("❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴡᴇᴇᴋʟʏ.", show_alert=True)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ sʜᴏᴡ_ᴡᴇᴇᴋʟʏ_ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ: {e}")
        await query.answer("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.", show_alert=True)


async def show_overall_leaderboard(query):
    try:
        chat_id = query.message.chat.id
        
        # ғɪʟᴛᴇʀ ʙʏ ᴄʜᴀᴛ_ɪᴅ ғᴏʀ ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ
        top_members = collection.find({"chat_id": chat_id}).sort("total_messages", -1).limit(10)

        response = "**✦ ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ 🏅**\n\n"
        count = 0
        for idx, member in enumerate(top_members, start=1):
            uid = member["user_id"]
            total = member["total_messages"]
            try:
                user = await app.get_users(uid)
                user_mention = f"[{user.first_name}](tg://user?id={uid})"
            except (PeerIdInvalid, UserNotParticipant):
                user_mention = f"`{uid}`"
            except Exception:
                user_mention = f"`{uid}`"
                
            response += f"**{idx}**. {user_mention} ➠ {total} ᴍsɢ\n"
            count += 1

        if count > 0:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_today"),
                 InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_weekly")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="rank_back_to_panel")]
            ])
            await query.message.edit_text(response, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await query.answer("❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴏᴠᴇʀᴀʟʟ.", show_alert=True)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ sʜᴏᴡ_ᴏᴠᴇʀᴀʟʟ_ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ: {e}")
        await query.answer("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.", show_alert=True)


@app.on_callback_query(filters.regex("^rank_(today|weekly|overall|back_to_panel)$"))
async def regular_callback_handler(_, query):
    try:
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
**✦ ᴄʜᴏᴏsᴇ ᴀ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴛʏᴘᴇ 🏅**

**⊚ ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴄʜᴇᴄᴋ ʙʏ ➠**

`/today` ➠ ᴛᴏᴅᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.
`/weekly` ➠ ᴡᴇᴇᴋʟʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.
`/overall` ➠ ᴀʟʟ ᴛɪᴍᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.

**➻ ʙʏ ➠ {bot_mention}**
            """

            buttons = InlineKeyboardMarkup([
            [
             InlineKeyboardButton("📊 ᴛᴏᴅᴀʏ", callback_data="rank_panel_today"),
             InlineKeyboardButton("📈 ᴡᴇᴇᴋʟʏ", callback_data="rank_panel_weekly")
            ],
            
            [
             InlineKeyboardButton("🏅 ᴏᴠᴇʀᴀʟʟ", callback_data="rank_panel_overall"),
             InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="rank_back_to_main")
            ]
        ])

            try:
                await query.message.edit_text(caption, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)
            except:
                await query.answer()
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ʀᴇɢᴜʟᴀʀ_ᴄᴀʟʟʙᴀᴄᴋ_ʜᴀɴᴅʟᴇʀ: {e}")
        await query.answer("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.", show_alert=True)


@app.on_callback_query(filters.regex("^rank_back_to_main$"))
async def back_to_main_handler(_, query):
    try:
        group_name = query.message.chat.title
        bot_mention = get_bot_mention()
        caption = f"""
**✦ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴘᴀɴɴᴇʟ 🏆**

**⊚ ɢʀᴏᴜᴘ ➠** {group_name}

**⊚ ᴄʜᴇᴄᴋ ɢʀᴏᴜᴘ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ʙʏ ᴛᴀᴘ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ↓**

**➻ ʙʏ ➠ {bot_mention}**
        """

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="rank_show_leaderboard_buttons")]
        ])

        await query.message.edit_text(caption, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ɪɴ ʙᴀᴄᴋ_ᴛᴏ_ᴍᴀɪɴ_ʜᴀɴᴅʟᴇʀ: {e}")
        await query.answer("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.", show_alert=True)


try:
    asyncio.create_task(daily_reset_scheduler())
    asyncio.create_task(weekly_reset_scheduler())
    print("ʀᴀɴᴋɪɴɢ sʏsᴛᴇᴍ sᴛᴀʀᴛᴇᴅ ᴡɪᴛʜ ʀᴇsᴇᴛ sᴄʜᴇᴅᴜʟᴇʀs")
except Exception as e:
    print(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴛᴀʀᴛ ʀᴇsᴇᴛ sᴄʜᴇᴅᴜʟᴇʀs: {e}") 
