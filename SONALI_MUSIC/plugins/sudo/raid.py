import time
from pyrogram import filters
from pyrogram.types import Message
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import SUDOERS

@app.on_message(filters.command("raid", prefixes=".") & SUDOERS)
async def raid_command(client, message: Message):
    try:
        await message.delete()
    except:
        pass

    if message.reply_to_message or len(message.command) > 1:
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user.mention()
            args = message.text.split(maxsplit=1)
            if len(args) > 1:
                try:
                    count, text_to_spam = args[1].split(maxsplit=1)
                    count = int(count)
                except ValueError:
                    count = 5
                    text_to_spam = args[1]
            else:
                count = 5
                text_to_spam = "Sᴘᴀᴍ!"
        else:
            user_arg = message.command[1]
            try:
                user = await client.get_users(user_arg)
                target_user = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            except:
                await message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ.")
                return

            try:
                count = int(message.command[2])
            except:
                count = 5

            try:
                text_to_spam = " ".join(message.command[3:])
            except:
                text_to_spam = "Sᴘᴀᴍ!"

        for _ in range(count):
            await message.reply_text(f"{target_user} **{text_to_spam}**")
            time.sleep(1)
    else:
        await message.reply_text(
            "⚠️ **ᴜsᴀɢᴇ :-** `.raid id count text`"
        )
