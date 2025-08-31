import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from SONALI_MUSIC import app

@app.on_chat_join_request()
async def join_request_handler(client, join_req):
    chat = join_req.chat
    user = join_req.from_user

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

    sent = await client.send_message(chat.id, text, reply_markup=buttons)

    # ⏳ 10 minutes (600 sec) baad auto delete
    await asyncio.sleep(600)
    try:
        await client.delete_messages(chat.id, sent.id)
    except:
        pass


# 🔘 Callback handle karega
@app.on_callback_query(filters.regex("^(approve|dismiss):"))
async def callback_handler(client: Client, query: CallbackQuery):
    action, chat_id, user_id = query.data.split(":")
    chat_id = int(chat_id)
    user_id = int(user_id)

    # check admin
    member = await client.get_chat_member(chat_id, query.from_user.id)
    if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ 😜", show_alert=True)

    if action == "approve":
        try:
            await client.approve_chat_join_request(chat_id, user_id)
            await query.edit_message_text(f"✅ ᴀᴘᴘʀᴏᴠᴇᴅ [ᴜsᴇʀ](tg://user?id={user_id})")
        except Exception as e:
            await query.answer(f"⚠️ ᴇʀʀᴏʀ : {e}", show_alert=True)

    elif action == "dismiss":
        try:
            await client.decline_chat_join_request(chat_id, user_id)
            await query.edit_message_text(f"❌ ᴅɪsᴍɪssᴇᴅ [ᴜsᴇʀ](tg://user?id={user_id})")
        except Exception as e:
            await query.answer(f"⚠️ ᴇʀʀᴏʀ : {e}", show_alert=True)
