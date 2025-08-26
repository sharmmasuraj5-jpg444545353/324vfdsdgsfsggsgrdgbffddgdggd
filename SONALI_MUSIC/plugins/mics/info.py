import datetime
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from SONALI_MUSIC import app

INFO_TEXT = """
<u><b>👤 ᴜꜱᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>

<b>● ᴘʀᴏғɪʟᴇ ᴘɪᴄ ➠</b> [ᴄʟɪᴄᴋ ʜᴇʀᴇ]({})
<b>● ᴜꜱᴇʀ ɪᴅ ➠</b> <code>{}</code>
<b>● ᴜꜱᴇʀɴᴀᴍᴇ ➠</b> <code>@{}</code>
<b>● ᴍᴇɴᴛɪᴏɴ ➠</b> {}
<b>● ꜱᴛᴀᴛᴜꜱ ➠</b> {}
<b>● ᴅᴄ ɪᴅ ➠</b> {}
<b>● ᴄʀᴇᴀᴛᴇᴅ ᴏɴ ➠</b> {}
<b>● ᴘʀᴇᴍɪᴜᴍ ➠</b> {}
<b>● ꜱᴄᴀᴍ ➠</b> {}
"""

# --- decode user_id into created date ---
def get_creation_date(user_id: int):
    telegram_epoch = 1514764800000
    timestamp = (user_id >> 32) + telegram_epoch
    return datetime.datetime.utcfromtimestamp(timestamp / 1000)

# --- user online status ---
async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "ʀᴇᴄᴇɴᴛʟʏ"
        elif x == enums.UserStatus.LAST_WEEK:
            return "ʟᴀꜱᴛ ᴡᴇᴇᴋ"
        elif x == enums.UserStatus.LONG_AGO:
            return "ʟᴏɴɢ ᴀɢᴏ"
        elif x == enums.UserStatus.OFFLINE:
            return "ᴏꜰꜰʟɪɴᴇ"
        elif x == enums.UserStatus.ONLINE:
            return "ᴏɴʟɪɴᴇ"
    except:
        return "❌ ᴇʀʀᴏʀ"

# --- main command handler ---
@app.on_message(filters.command(["info", "information", "userinfo", "whois"], prefixes=["/", "!"]))
async def userinfo(_, message: Message):
    chat_id = message.chat.id

    try:
        user_id = None

        # case: /info user_id | username
        if not message.reply_to_message and len(message.command) == 2:
            user_id = message.text.split(None, 1)[1]

        # case: reply to someone
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id

        # case: no input - show own info
        else:
            user_id = message.from_user.id

        # get user info
        user = await app.get_users(user_id)
        status = await userstatus(user.id)
        creation_date = get_creation_date(user.id).strftime("%d-%m-%Y %H:%M:%S")

        scam = "⚠️ ʏᴇꜱ" if user.is_scam else "✅ ɴᴏ"
        premium = "✅ ʏᴇꜱ" if user.is_premium else "❌ ɴᴏ"

        if user.username:
            profile_url = f"https://t.me/{user.username}"
        else:
            profile_url = f"tg://user?id={user.id}"

        # FIXED: Safe profile photo handling
        photo_link = profile_url  # Default to profile URL
        
        try:
            # Check if the app object has the get_profile_photos method
            if hasattr(app, 'get_profile_photos'):
                # Get user's profile photos
                photos = await app.get_profile_photos(user.id, limit=1)
                
                if photos.total_count > 0:
                    # Get the file_id of the first (most recent) profile photo
                    file_id = photos.photos[0][-1].file_id
                    
                    # Send the photo temporarily to get a message ID
                    sent_message = await app.send_photo(chat_id, file_id, caption="Processing...")
                    
                    # Generate the direct link to the photo
                    if str(chat_id).startswith("-100"):
                        # For supergroups/channels
                        photo_link = f"https://t.me/c/{str(chat_id)[4:]}/{sent_message.id}"
                    else:
                        # For private chats
                        photo_link = f"https://t.me/c/{str(chat_id)[1:]}/{sent_message.id}"
                    
                    # Delete the temporary message
                    await sent_message.delete()
            else:
                # If get_profile_photos method doesn't exist, use alternative approach
                photo_link = profile_url
        except Exception as e:
            print(f"Error getting profile photo: {e}")
            # If anything fails, use the profile URL as fallback

        # send info
        await message.reply_text(
            text=INFO_TEXT.format(
                photo_link,
                user.id,
                user.username or "N/A",
                user.mention,
                status,
                user.dc_id or "N/A",
                creation_date,
                premium,
                scam,
            ),
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(f"{user.first_name}", url=profile_url),
                    InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")
                ]]
            ),
            disable_web_page_preview=True,
        )

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
