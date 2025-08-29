from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SONALI_MUSIC import app


@app.on_callback_query()
async def unpin_callback(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat = callback_query.message.chat

    if chat.type not in ["group", "supergroup"]:
        return await callback_query.answer(
            "⚠ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!",
            show_alert=True
        )

    member = await chat.get_member(user_id)

    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] \
       or not member.privileges.can_pin_messages:
        return await callback_query.answer(
            "⚠ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛs ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs!",
            show_alert=True
        )

    if data.startswith("delete_btn"):
        return await callback_query.message.delete()

    if data.startswith("unpin="):
        action = data.split("=")[1]

        if action == "yes":
            await client.unpin_all_chat_messages(chat.id)
            textt = "**✅ ᴀʟʟ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴᴘɪɴɴᴇᴅ!**"
        elif action == "no":
            textt = "**❌ ᴏᴋᴀʏ, ɪ ᴡɪʟʟ ɴᴏᴛ ᴜɴᴘɪɴ ᴀɴʏᴛʜɪɴɢ.**"
        else:
            try:
                msg_id = int(action)
                await client.unpin_chat_message(chat.id, msg_id)
                textt = "**✅ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴜɴᴘɪɴɴᴇᴅ!**"
            except:
                textt = "**⚠ ғᴀɪʟᴇᴅ ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇ.**"

        await callback_query.message.edit_caption(
            textt,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ", callback_data="delete_btn=admin")]]
            )
        )


@app.on_message(filters.command(["unpinall"]) & filters.group)
async def unpinall_command(client, message):
    chat = message.chat
    admin_id = message.from_user.id
    member = await chat.get_member(admin_id)

    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] \
       or not member.privileges.can_pin_messages:
        return await message.reply_text(
            "**⚠ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs.**"
        )

    await message.reply_text(
        "**❓ ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜɴᴘɪɴ ᴀʟʟ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ?**",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("✔ ʏᴇs", callback_data="unpin=yes"),
                InlineKeyboardButton("✖ ɴᴏ", callback_data="unpin=no")
            ]]
        )
    )
