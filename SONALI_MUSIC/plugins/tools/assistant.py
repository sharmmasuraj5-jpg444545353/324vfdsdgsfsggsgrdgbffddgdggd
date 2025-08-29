from SONALI_MUSIC import assistants
from SONALI_MUSIC import userbot as us, app
from pyrogram import filters
from pyrogram.types import Message
from SONALI_MUSIC.misc import SUDOERS
from config import BANNED_USERS, OWNER_ID


@app.on_message(filters.command(["asspfp", "setpfp"]) & filters.user(OWNER_ID))
async def set_pfp(_, message: Message):
    if message.reply_to_message.photo:
        fuk = await message.reply_text("**ɴᴏ ᴄʜᴀɴɢɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛ'ꜱ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄ...**")
        img = await message.reply_to_message.download()
        if 1 in assistants:
            ubot = us.one
        try:
            await ubot.set_profile_photo(photo=img)
            return await fuk.edit_text(
                f"**» {ubot.me.mention} ᴘʀᴏꜰɪʟᴇ ᴘɪᴄ ᴄʜᴀɴɢᴇᴅ ꜱᴜᴄᴄᴇssꜰᴜʟʟʏ..**"
            )
        except:
            return await fuk.edit_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄʜᴀɴɢᴇ ᴀꜱꜱɪꜱᴛᴀɴᴛ'ꜱ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄ.**")
    else:
        await message.reply_text(
            "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ꜰᴏʀ ᴄʜᴀɴɢɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛ'ꜱ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄ..**"
        )



@app.on_message(filters.command(["delpfp", "delasspfp"]) & filters.user(OWNER_ID))
async def del_pfp(_, message: Message):
    try:
        if 1 in assistants:
            ubot = us.one
        pfp = [p async for p in ubot.get_chat_photos("me")]
        await ubot.delete_profile_photos(pfp[0].file_id)
        return await message.reply_text("**ꜱᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴀꜱꜱɪꜱᴛᴀɴᴛ'ꜱ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄ.**")
    except Exception as ex:
        await message.reply_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜱꜱɪꜱᴛᴀɴᴛ'ꜱ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄ.**")



@app.on_message(filters.command(["assbio", "setbio"]) & filters.user(OWNER_ID))
async def set_bio(_, message: Message):
    msg = message.reply_to_message
    if msg and msg.text:
        newbio = msg.text
        if 1 in assistants:
            ubot = us.one
        await ubot.update_profile(bio=newbio)
        return await message.reply_text(f"**» {ubot.me.mention} ʙɪᴏ ᴄʜᴀɴɢᴇᴅ ꜱᴜᴄᴄᴇssꜰᴜʟʟʏ.**")
    elif len(message.command) != 1:
        newbio = message.text.split(None, 1)[1]
        if 1 in assistants:
            ubot = us.one
        await ubot.update_profile(bio=newbio)
        return await message.reply_text(f"**» {ubot.me.mention} ʙɪᴏ ᴄʜᴀɴɢᴇᴅ ꜱᴜᴄᴄᴇssꜰᴜʟʟʏ.**")
    else:
        return await message.reply_text(
            "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ɪᴛ ᴀꜱ ᴀꜱꜱɪꜱᴛᴀɴᴛ'ꜱ ʙɪᴏ.**"
        )



@app.on_message(filters.command(["assname", "setname"]) & filters.user(OWNER_ID))
async def set_name(_, message: Message):
    msg = message.reply_to_message
    if msg and msg.text:
        name = msg.text
        if 1 in assistants:
            ubot = us.one
        await ubot.update_profile(first_name=name)
        return await message.reply_text(f"**» {ubot.me.mention} ɴᴀᴍᴇ ᴄʜᴀɴɢᴇᴅ ꜱᴜᴄᴄᴇssꜰᴜʟʟʏ.**")
    elif len(message.command) != 1:
        name = message.text.split(None, 1)[1]
        if 1 in assistants:
            ubot = us.one
        await ubot.update_profile(first_name=name, last_name="")
        return await message.reply_text(f"**» {ubot.me.mention} ɴᴀᴍᴇ ᴄʜᴀɴɢᴇᴅ ꜱᴜᴄᴄᴇssꜰᴜʟʟʏ.**")
    else:
        return await message.reply_text(
            "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ɪᴛ ᴀꜱ ᴀꜱꜱɪꜱᴛᴀɴᴛ'ꜱ ɴᴇᴡ ɴᴀᴍᴇ.**"
        )
