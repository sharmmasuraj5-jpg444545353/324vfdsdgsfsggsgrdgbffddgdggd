from pyrogram import Client, filters
from pyrogram.types import ChatPrivileges
from SONALI_MUSIC import app

@app.on_chat_member_updated()
async def video_chat_event(client, update):
    if update.new_chat_member and update.new_chat_member.privileges:
        if update.new_chat_member.privileges.can_manage_video_chats:
            user = update.new_chat_member.user
            chat_id = update.chat.id
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            username = f"@{user.username}" if user.username else "No Username"
            user_id = user.id

            message = f"🎥 **New User Joined Video Chat**\n\n👤 Name: {mention}\n🆔 User ID: `{user_id}`\n🔗 Username: {username}"
            
            await client.send_message(chat_id, message)
