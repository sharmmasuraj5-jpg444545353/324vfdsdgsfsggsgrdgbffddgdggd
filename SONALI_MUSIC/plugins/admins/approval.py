from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pymongo import MongoClient
import asyncio
from datetime import datetime

from SONALI_MUSIC import app

# MongoDB setup
mongo = MongoClient("mongodb+srv://Rishant:Thakur@cluster0.g5kjakc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo["JOIN_REQUEST_DB"]
col = db["requests"]


# 🚨 जब भी कोई नई join request आए
@app.on_chat_join_request()
async def join_request_handler(client, join_req):
    chat = join_req.chat
    user = join_req.from_user
    
    # Pehle check karo ki user already member to nahi hai
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            # Agar already member hai to request delete karo
            col.delete_one({"chat_id": chat.id, "user_id": user.id})
            return
    except:
        pass
    
    # Check if user already has a pending request
    existing_request = col.find_one({
        "chat_id": chat.id, 
        "user_id": user.id
    })
    
    if existing_request:
        # Agar already request hai to naya button mat bhejo
        print(f"Duplicate request ignored for user {user.id} in chat {chat.id}")
        return
    
    # MongoDB me save
    col.update_one(
        {"chat_id": chat.id, "user_id": user.id},
        {"$set": {
            "chat_id": chat.id, 
            "user_id": user.id, 
            "username": user.username,
            "first_name": user.first_name,
            "status": "pending",
            "timestamp": datetime.now()
        }},
        upsert=True,
    )

    text = (
        "🚨 ᴀ ɴᴇᴡ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ғᴏᴜɴᴅ ❕\n\n"
        f"👤 ᴜsᴇʀ : {user.mention}\n"
        f"🆔 ɪᴅ : `{user.id}`\n"
        f"🔗 ᴜsᴇʀɴᴀᴍᴇ : @{user.username if user.username else 'ɴᴏɴᴇ'}"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"approve:{chat.id}:{user.id}"),
                InlineKeyboardButton("❌ ᴅɪsᴍɪss", callback_data=f"dismiss:{chat.id}:{user.id}")
            ]
        ]
    )

    await client.send_message(chat.id, text, reply_markup=buttons)


# 🔘 Callback handle karega - FIXED VERSION
@app.on_callback_query(filters.regex("^(approve|dismiss):"))
async def callback_handler(client: Client, query: CallbackQuery):
    action, chat_id, user_id = query.data.split(":")
    chat_id = int(chat_id)
    user_id = int(user_id)

    # check admin
    try:
        member = await client.get_chat_member(chat_id, query.from_user.id)
        if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʙᴀʙʏ 😜", show_alert=True)
    except:
        return await query.answer("⚠️ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ ғᴀɪʟᴇᴅ", show_alert=True)

    if action == "approve":
        try:
            # Pehle check karo ki user already member to nahi hai
            try:
                existing_member = await client.get_chat_member(chat_id, user_id)
                if existing_member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    await query.edit_message_text(f"✅ ᴜsᴇʀ ᴀʟʀᴇᴀᴅʏ ᴍᴇᴍʙᴇʀ")
                    col.delete_one({"chat_id": chat_id, "user_id": user_id})
                    return
            except:
                pass
                
            await client.approve_chat_join_request(chat_id, user_id)
            col.delete_one({"chat_id": chat_id, "user_id": user_id})
            await query.edit_message_text(f"✅ ᴀᴘᴘʀᴏᴠᴇᴅ [ᴜsᴇʀ](tg://user?id={user_id})")
        except Exception as e:
            await query.answer(f"⚠️ ᴇʀʀᴏʀ : {str(e)}", show_alert=True)

    elif action == "dismiss":
        try:
            await client.decline_chat_join_request(chat_id, user_id)
            col.delete_one({"chat_id": chat_id, "user_id": user_id})
            await query.edit_message_text(f"❌ ᴅɪsᴍɪssᴇᴅ [ᴜsᴇʀ](tg://user?id={user_id})")
        except Exception as e:
            await query.answer(f"⚠️ ᴇʀʀᴏʀ : {str(e)}", show_alert=True)


# -------- Commands for all -------- #

# ✅ Approve all - FIXED VERSION
@app.on_message(filters.command("approveall") & filters.group)
async def approve_all(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # check admin
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ❕")
    except:
        return await message.reply_text("❌ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ ғᴀɪʟᴇᴅ")

    # MongoDB se saari pending requests fetch karo
    pending_requests = list(col.find({"chat_id": chat_id}))
    
    # Check if no requests found
    if not pending_requests:
        return await message.reply_text("❌ ɴᴏ ᴘᴇɴᴅɪɴɢ ʀᴇǫᴜᴇsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ ❕")
    
    count = 0
    failed = 0
    for request in pending_requests:
        try:
            user_id_to_approve = request["user_id"]
            
            # Pehle check karo ki user already member to nahi hai
            try:
                existing_member = await app.get_chat_member(chat_id, user_id_to_approve)
                if existing_member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    col.delete_one({"chat_id": chat_id, "user_id": user_id_to_approve})
                    continue
            except:
                pass
                
            await app.approve_chat_join_request(chat_id, user_id_to_approve)
            col.delete_one({"chat_id": chat_id, "user_id": user_id_to_approve})
            count += 1
            await asyncio.sleep(0.5)  # Rate limit avoid karne ke liye
        except Exception as e:
            print(f"Error approving user {request['user_id']}: {e}")
            failed += 1
            continue

    await message.reply_text(f"✅ ᴀᴄᴄᴇᴘᴛɪɴɢ ʀᴇǫᴜᴇsᴛs sᴛᴀʀᴛᴇᴅ ʙʏ {message.from_user.mention}\n\n✅ {count} ᴀᴘᴘʀᴏᴠᴇᴅ\n❌ {failed} ғᴀɪʟᴇᴅ")


# ❌ Dismiss all - FIXED VERSION
@app.on_message(filters.command("dismissall") & filters.group)
async def dismiss_all(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # check admin
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ❕")
    except:
        return await message.reply_text("❌ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ ғᴀɪʟᴇᴅ")

    # MongoDB se saari pending requests fetch karo
    pending_requests = list(col.find({"chat_id": chat_id}))
    
    # Check if no requests found
    if not pending_requests:
        return await message.reply_text("❌ ɴᴏ ᴘᴇɴᴅɪɴɢ ʀᴇǫᴜᴇsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ ❕")
    
    count = 0
    failed = 0
    for request in pending_requests:
        try:
            user_id_to_dismiss = request["user_id"]
            await app.decline_chat_join_request(chat_id, user_id_to_dismiss)
            col.delete_one({"chat_id": chat_id, "user_id": user_id_to_dismiss})
            count += 1
            await asyncio.sleep(0.5)  # Rate limit avoid karne ke liye
        except Exception as e:
            print(f"Error dismissing user {request['user_id']}: {e}")
            failed += 1
            continue

    await message.reply_text(f"❌ ᴅɪsᴍɪssɪɴɢ ʀᴇǫᴜᴇsᴛs sᴛᴀʀᴛᴇᴅ ʙʏ {message.from_user.mention}\n\n✅ {count} ᴅɪsᴍɪssᴇᴅ\n❌ {failed} ғᴀɪʟᴇᴅ")


# 📊 Status check command
@app.on_message(filters.command("pending") & filters.group)
async def pending_requests(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # check admin
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ❕")
    except:
        return await message.reply_text("❌ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ ғᴀɪʟᴇᴅ")

    # MongoDB se pending requests count karo
    pending_count = col.count_documents({"chat_id": chat_id})
    
    await message.reply_text(f"📊 ᴘᴇɴᴅɪɴɢ ʀᴇǫᴜᴇsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ: {pending_count}")
