
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from SONALI_MUSIC import app

# Temporary storage for active buttons
active_buttons = {}

@app.on_chat_join_request()
async def join_request_handler(client, join_req):
    chat = join_req.chat
    user = join_req.from_user
    
    # ✅ Check if this user already has an active button
    request_key = f"{chat.id}_{user.id}"
    if request_key in active_buttons:
        return  # Agar already button hai to naya mat bhejo
    
    # Mark this button as active
    active_buttons[request_key] = True

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

    # ⏳ 10 minutes (600 sec) baad auto delete aur active_buttons se remove
    async def delete_and_cleanup():
        await asyncio.sleep(600)
        try:
            await client.delete_messages(chat.id, sent.id)
        except:
            pass
        finally:
            # Button ko active list se remove karo
            if request_key in active_buttons:
                del active_buttons[request_key]

    # Background task start karo
    asyncio.create_task(delete_and_cleanup())


# 🔘 Callback handle karega
@app.on_callback_query(filters.regex("^(approve|dismiss):"))
async def callback_handler(client: Client, query: CallbackQuery):
    action, chat_id, user_id = query.data.split(":")
    chat_id = int(chat_id)
    user_id = int(user_id)

    # check admin
    try:
        member = await client.get_chat_member(chat_id, query.from_user.id)
        if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ 😜", show_alert=True)
    except:
        return await query.answer("⚠️ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ ғᴀɪʟᴇᴅ", show_alert=True)

    if action == "approve":
        try:
            await client.approve_chat_join_request(chat_id, user_id)
            
            # ✅ User ko personal message bhejo
            try:
                chat_obj = await client.get_chat(chat_id)
                user_obj = await client.get_users(user_id)
                await client.send_message(
                    user_id,
                    f"🎉 **ᴅᴇᴀʀ {user_obj.mention}, ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ :-** `{chat_obj.title}`"
                )
            except:
                pass
            
            await query.edit_message_text(f"✅ ᴀᴘᴘʀᴏᴠᴇᴅ {query.from_user.mention} ɪɴ ᴛʜɪs ᴄʜᴀᴛ")
            
        except Exception as e:
            error_msg = str(e)
            if "already handled" in error_msg.lower():
                await query.edit_message_text("✅ ʀᴇǫᴜᴇsᴛ ᴀʟʀᴇᴀᴅʏ ʜᴀɴᴅʟᴇᴅ")
            else:
                await query.answer(f"⚠️ ᴇʀʀᴏʀ : {error_msg}", show_alert=True)

    elif action == "dismiss":
        try:
            await client.decline_chat_join_request(chat_id, user_id)
            await query.edit_message_text(f"❌ ᴅɪsᴍɪssᴇᴅ {query.from_user.mention} ɪɴ ᴛʜɪs ᴄʜᴀᴛ")
        except Exception as e:
            error_msg = str(e)
            if "already handled" in error_msg.lower():
                await query.edit_message_text("❌ ʀᴇǫᴜᴇsᴛ ᴀʟʀᴇᅳʏ ʜᴀɴᴅʟᴇᴅ")
            else:
                await query.answer(f"⚠️ ᴇʀʀᴏʀ : {error_msg}", show_alert=True)
    
    # ✅ Button ko active list se REMOVE karo taaki naya button aa sake
    request_key = f"{chat_id}_{user_id}"
    if request_key in active_buttons:
        del active_buttons[request_key]
