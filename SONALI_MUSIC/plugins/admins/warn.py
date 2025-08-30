import asyncio
from contextlib import suppress

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    ChatPrivileges,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from string import ascii_lowercase
from typing import Dict, Union

from SONALI_MUSIC import app
from SONALI_MUSIC.misc import SUDOERS
from SONALI_MUSIC.core.mongo import mongodb
from SONALI_MUSIC.utils.error import capture_err
from SONALI_MUSIC.utils.keyboard import ikb
from SONALI_MUSIC.utils.database import save_filter
from SONALI_MUSIC.utils.functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)
from utils.permissions import adminsOnly, member_permissions
from config import BANNED_USERS



warnsdb = mongodb.warns


async def int_to_alpha(user_id: int) -> str:
    alphabet = list(ascii_lowercase)[:10]
    text = ""
    user_id = str(user_id)
    for i in user_id:
        text += alphabet[int(i)]
    return text


async def get_warns_count() -> dict:
    chats_count = 0
    warns_count = 0
    async for chat in warnsdb.find({"chat_id": {"$lt": 0}}):
        for user in chat["warns"]:
            warns_count += chat["warns"][user]["warns"]
        chats_count += 1
    return {"chats_count": chats_count, "warns_count": warns_count}


async def get_warns(chat_id: int) -> Dict[str, int]:
    warns = await warnsdb.find_one({"chat_id": chat_id})
    if not warns:
        return {}
    return warns["warns"]


async def get_warn(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    if name in warns:
        return warns[name]


async def add_warn(chat_id: int, name: str, warn: dict):
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    warns[name] = warn

    await warnsdb.update_one(
        {"chat_id": chat_id}, {"$set": {"warns": warns}}, upsert=True
    )


async def remove_warns(chat_id: int, name: str) -> bool:
    warnsd = await get_warns(chat_id)
    name = name.lower().strip()
    if name in warnsd:
        del warnsd[name]
        await warnsdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"warns": warnsd}},
            upsert=True,
        )
        return True
    return False

@app.on_message(filters.command(["kick", "skick"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def kickFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("ɪ ᴄᴀɴ'ᴛ ғɪɴᴅ ᴛʜᴀᴛ ᴜsᴇʀ")
    if user_id == app.id:
        return await message.reply_text("ɪ ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ᴍʏsᴇʟғ, ɪ ᴄᴀɴ ʟᴇᴀᴠᴇ ɪғ ʏᴏᴜ ᴡᴀɴᴛ.")
    if user_id in SUDOERS:
        return await message.reply_text("ʏᴏᴜ ᴡᴀɴɴᴀ ᴋɪᴄᴋ ᴛʜᴇ ᴇʟᴇᴠᴀᴛᴇᴅ ᴏɴᴇ ?")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text(
            "ɪ ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ᴀɴ ᴀᴅᴍɪɴ, ʏᴏᴜ ᴋɴᴏᴡ ᴛʜᴇ ʀᴜʟᴇs, ʏᴏᴜ ᴋɴᴏᴡ ᴛʜᴇ ʀᴜʟᴇs, sᴏ ᴅᴏ ɪ "
        )
    mention = (await app.get_users(user_id)).mention
    msg = f"""
**ᴋɪᴄᴋᴇᴅ ᴜsᴇʀ:** {mention}
**ᴋɪᴄᴋᴇᴅ ʙʏ:** {message.from_user.mention if message.from_user else 'ᴀɴᴏɴᴍᴏᴜs'}
**ʀᴇᴀsᴏɴ:** {reason or 'ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ'}"""
    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg)
    await asyncio.sleep(1)
    await message.chat.unban_member(user_id)
    if message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)


@app.on_message(filters.command(["warn", "swarn"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def warn_user(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text("ɪ ᴄᴀɴᴛ ғɪɴᴅ ᴛʜᴀᴛ ᴜsᴇʀ")
    if user_id == app.id:
        return await message.reply_text("ɪ ᴄᴀɴ'ᴛ ᴡᴀʀɴ ᴍʏsᴇʟғ, ɪ ᴄᴀɴ ʟᴇᴀᴠᴇ ɪғ ʏᴏᴜ ᴡᴀɴᴛ.")
    if user_id in SUDOERS:
        return await message.reply_text(
            "ɪ ᴄᴀɴ'ᴛ ᴡᴀʀɴ ᴍʏ ᴍᴀɴᴀɢᴇʀ's, ʙᴇᴄᴀᴜsᴇ ʜᴇ ᴍᴀɴᴀɢᴇ ᴍᴇ!"
        )
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text(
            "ɪ ᴄᴀɴ'ᴛ ᴡᴀʀɴ ᴀɴ ᴀᴅᴍɪɴ, ʏᴏᴜ ᴋɴᴏᴡ ᴛʜᴇ ʀᴜʟᴇs sᴏ ᴅᴏ ɪ."
        )
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({"🚨  ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴ  🚨": f"unwarn_{user_id}"})
    if warns:
        warns = warns["warns"]
    else:
        warns = 0
    if message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(f"ɴᴜᴍʙᴇʀ ᴏғ ᴡᴀʀɴs ᴏғ {mention} ᴇxᴄᴇᴇᴅᴇᴅ, ʙᴀɴɴᴇᴅ!")
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        msg = f"""
**ᴡᴀʀɴᴇᴅ ᴜsᴇʀ:** {mention}
**ᴡᴀʀɴᴇᴅ ʙʏ:** {message.from_user.mention if message.from_user else 'ᴀɴᴏɴᴍᴏᴜs'}
**ʀᴇᴀsᴏɴ :** {reason or 'ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠᴏᴅᴇᴅ'}
**ᴡᴀʀɴs:** {warns + 1}/3"""
        replied_message = message.reply_to_message
        if replied_message:
            message = replied_message
        await message.reply_text(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_") & ~BANNED_USERS)
async def remove_warning(_, cq: CallbackQuery):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ\n"
            + f"ᴘᴇʀᴍɪssɪᴏɴ ɴᴇᴇᴅᴇᴅ: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer("ᴜsᴇʀ ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs.")
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__ᴡᴀʀɴ ʀᴇᴍᴏᴠᴇᴅ ʙʏ {from_user.mention}__"
    await cq.message.edit(text)


@app.on_message(filters.command("rmwarns") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def remove_warnings(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    mention = (await app.get_users(user_id)).mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if warns == 0 or not warns:
        await message.reply_text(f"{mention} ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs.")
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(f"ʀᴇᴍᴏᴠᴇᴅ ᴡᴀʀɴɪɴɢs ᴏғ {mention}.")


@app.on_message(filters.command("warns") & ~filters.private & ~BANNED_USERS)
@capture_err
async def check_warns(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("ɪ ᴄᴀɴ'ᴛ ғɪɴᴅ ᴛʜᴀᴛ ᴜsᴇʀ.")
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    if warns:
        warns = warns["warns"]
    else:
        return await message.reply_text(f"{mention} ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs.")
    return await message.reply_text(f"{mention} ʜᴀs {warns}/3 ᴡᴀʀɴɪɴɢs")
