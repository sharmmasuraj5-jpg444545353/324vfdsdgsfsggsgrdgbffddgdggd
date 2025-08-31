from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pymongo import MongoClient
import asyncio

from SONALI_MUSIC import app

mongo = MongoClient("mongodb+srv://Rishant:Thakur@cluster0.g5kjakc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo["JOIN_REQUEST_DB"]
col = db["requests"]


# जब भी कोई join request आए
@app.on_chat_join_request()
async def join_request_handler(client, join_req):
    chat = join_req.chat
    user = join_req.from_user

    # MongoDB me save
    col.update_one(
        {"chat_id": chat.id, "user_id": user.id},
        {"$set": {"chat_id": chat.id, "user_id": user.id, "username": user.username}},
        upsert=True,
    )

    text = (
        "🚨 𝗔 𝗻𝗲𝘄 𝗷𝗼𝗶𝗻 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 𝗳𝗼𝘂𝗻𝗱 ❕\n\n"
        f"👤 𝗨𝘀𝗲𝗿 : {user.mention}\n"
        f"🆔 𝗜𝗗 : `{user.id}`\n"
        f"🔗 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : @{user.username if user.username else '𝖓𝖔𝖓𝖊'}"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲", callback_data=f"approve:{chat.id}:{user.id}"),
                InlineKeyboardButton("❌ 𝗗𝗶𝘀𝗺𝗶𝘀𝘀", callback_data=f"dismiss:{chat.id}:{user.id}")
            ]
        ]
    )

    await client.send_message(chat.id, text, reply_markup=buttons)


# Callback handle karega
@app.on_callback_query(filters.regex("^(approve|dismiss):"))
async def callback_handler(client: Client, query: CallbackQuery):
    action, chat_id, user_id = query.data.split(":")
    chat_id = int(chat_id)
    user_id = int(user_id)

    # check admin
    member = await client.get_chat_member(chat_id, query.from_user.id)
    if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        return await query.answer("⚠️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗱𝗺𝗶𝗻 𝗯𝗮𝗯𝘆 😜", show_alert=True)

    if action == "approve":
        try:
            await client.approve_chat_join_request(chat_id, user_id)
            col.delete_one({"chat_id": chat_id, "user_id": user_id})
            await query.edit_message_text(f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 [𝗨𝘀𝗲𝗿](tg://user?id={user_id}) 𝗶𝗻 𝗰𝗵𝗮𝘁 ✅")
        except Exception as e:
            await query.answer(f"⚠️ 𝗘𝗿𝗿𝗼𝗿 : {e}", show_alert=True)

    elif action == "dismiss":
        try:
            await client.decline_chat_join_request(chat_id, user_id)
            col.delete_one({"chat_id": chat_id, "user_id": user_id})
            await query.edit_message_text(f"❌ 𝗗𝗶𝘀𝗺𝗶𝘀𝘀𝗲𝗱 [𝗨𝘀𝗲𝗿](tg://user?id={user_id}) 𝗳𝗿𝗼𝗺 𝗷𝗼𝗶𝗻 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 ❌")
        except Exception as e:
            await query.answer(f"⚠️ 𝗘𝗿𝗿𝗼𝗿 : {e}", show_alert=True)


# -------- Commands for all -------- #

@app.on_message(filters.command("approveall") & filters.group)
async def approve_all(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # check admin
    member = await app.get_chat_member(chat_id, user_id)
    if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        return await message.reply_text("❌ 𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 ❕")

    # Approve all pending
    async for req in app.get_chat_join_requests(chat_id):
        try:
            await app.approve_chat_join_request(chat_id, req.from_user.id)
            col.delete_one({"chat_id": chat_id, "user_id": req.from_user.id})
            await asyncio.sleep(0.2)
        except Exception:
            pass

    await message.reply_text(f"✅ 𝗔𝗰𝗰𝗲𝗽𝘁𝗶𝗻𝗴 𝗿𝗲𝗾𝘂𝗲𝘀𝘁𝘀 𝘀𝘁𝗮𝗿𝘁𝗲𝗱 𝗯𝘆 {message.from_user.mention}")


@app.on_message(filters.command("dismissall") & filters.group)
async def dismiss_all(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # check admin
    member = await app.get_chat_member(chat_id, user_id)
    if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        return await message.reply_text("❌ 𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 ❕")

    # Dismiss all pending
    async for req in app.get_chat_join_requests(chat_id):
        try:
            await app.decline_chat_join_request(chat_id, req.from_user.id)
            col.delete_one({"chat_id": chat_id, "user_id": req.from_user.id})
            await asyncio.sleep(0.2)
        except Exception:
            pass

    await message.reply_text(f"❌ 𝗗𝗶𝘀𝗺𝗶𝘀𝘀𝗶𝗻𝗴 𝗿𝗲𝗾𝘂𝗲𝘀𝘁𝘀 𝘀𝘁𝗮𝗿𝘁𝗲𝗱 𝗯𝘆 {message.from_user.mention}")
