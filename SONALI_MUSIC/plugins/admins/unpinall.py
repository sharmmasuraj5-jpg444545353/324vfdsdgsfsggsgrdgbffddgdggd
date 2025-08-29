from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SONALI_MUSIC import app

@app.on_callback_query(filters.regex(r"^unpin"))
async def unpin_callback(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    chat_id = CallbackQuery.message.chat.id
    member = await app.get_chat_member(chat_id, user_id)

    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or not member.privileges.can_pin_messages:
        await CallbackQuery.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛs ᴛᴏ ᴜɴᴘɪɴ, ʙᴋʟ", show_alert=True)
        return

    msg_id = CallbackQuery.data.split("=")[1]

    if msg_id == "yes":
        await client.unpin_all_chat_messages(chat_id)
        textt = "**✅ ᴀʟʟ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴᴘɪɴɴᴇᴅ!**"
    elif msg_id == "no":
        textt = "**❌ ᴏᴋᴀʏ, ɪ ᴡɪʟʟ ɴᴏᴛ ᴜɴᴘɪɴ ᴀɴʏᴛʜɪɴɢ.**"
    else:
        try:
            msg_id = int(msg_id)
            await client.unpin_chat_message(chat_id, msg_id)
            textt = "**✅ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴜɴᴘɪɴɴᴇᴅ!**"
        except:
            textt = "**⚠ ғᴀɪʟᴇᴅ ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇ.**"

    await CallbackQuery.message.edit_caption(
        textt,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="ᴅᴇʟᴇᴛᴇ", callback_data="delete_btn=admin")]]
        )
    )

@app.on_message(filters.command(["unpinall"]))
async def unpinall_command(client, message):
    chat_id = message.chat.id
    admin_id = message.from_user.id
    member = await message.chat.get_member(admin_id)

    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or not member.privileges.can_pin_messages:
        return await message.reply_text(
            "**⚠ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs.**"
        )

    await message.reply_text(
        "**❓ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜɴᴘɪɴ ᴀʟʟ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ?**",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text="✔ ʏᴇs", callback_data="unpin=yes"),
                InlineKeyboardButton(text="✖ ɴᴏ", callback_data="unpin=no")
            ]]
        )
    )
