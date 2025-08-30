import random
import asyncio
import json
from SONALI_MUSIC import app
from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from pymongo import MongoClient
from config import MONGO_DB_URI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    mongo_client = MongoClient(MONGO_DB_URI)
    db = mongo_client["welcome_db"]
    chat_settings = db["chat_settings"]
    mongo_client.admin.command('ping')
    logger.info("MongoDB connection successful")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    chat_settings = None

bot_ready = False

ShrutiWelcome = [
    "❖ <b>ʜᴇʏ {user} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!</b>",
    "❖ <b>ɢʟᴀᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ {user} ᴇɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.</b>",
    "❖ <b>ʜᴇʟʟᴏ {user}, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ғᴀᴍɪʟʏ!</b>",
    "❖ <b>ʜᴇʏᴀ {user}, ɢʟᴀᴅ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ ʜᴇʀᴇ!</b>",
    "❖ <b>ᴡᴇʟᴄᴏᴍᴇ {user} ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ! ʟᴇᴛ's ʜᴀᴠᴇ ғᴜɴ.</b>"
]

ShrutiLeft = [
    "❖ <b>ʙʏᴇ {user} sᴇᴇ ʏᴏᴜ sᴏᴏɴ.</b>",
    "❖ <b>{user} ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ... ɪᴛ ғᴇᴇʟs ᴇᴍᴘᴛʏ ᴡɪᴛʜᴏᴜᴛ ʏᴏᴜ.</b>",
    "❖ <b>{user} ʜᴀs ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ!</b>",
    "❖ <b>ɢᴏᴏᴅʙʏᴇ {user}, ʜᴏᴘᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ ᴀɢᴀɪɴ sᴏᴏɴ!</b>",
    "❖ <b>{user} ʜᴀs ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴛᴀᴋᴇ ᴄᴀʀᴇ!</b>"
]

last_welcome = {}
left_message_tasks = {}

def is_welcome_enabled(chat_id):
    """Check if welcome messages are enabled for a chat"""
    if chat_settings is None:
        return True
    try:
        setting = chat_settings.find_one({"chat_id": chat_id})
        return setting.get("welcome", True) if setting else True
    except Exception as e:
        logger.error(f"Error checking welcome status: {e}")
        return True

def is_left_enabled(chat_id):
    """Check if left messages are enabled for a chat"""
    if chat_settings is None:
        return True
    try:
        setting = chat_settings.find_one({"chat_id": chat_id})
        return setting.get("left", True) if setting else True
    except Exception as e:
        logger.error(f"Error checking left status: {e}")
        return True

def set_welcome(chat_id, value: bool):
    """Set welcome message status for a chat"""
    if chat_settings is None:
        return False
    try:
        chat_settings.update_one(
            {"chat_id": chat_id},
            {"$set": {"welcome": value}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error setting welcome status: {e}")
        return False

def set_left(chat_id, value: bool):
    """Set left message status for a chat"""
    if chat_settings is None:
        return False
    try:
        chat_settings.update_one(
            {"chat_id": chat_id},
            {"$set": {"left": value}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error setting left status: {e}")
        return False

async def is_admin(client, chat_id, user_id):
    """Check if user is admin in the chat"""
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER
        )
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def delete_previous_welcome(client, chat_id):
    """Delete previous welcome message if exists"""
    if chat_id in last_welcome:
        try:
            await client.delete_messages(chat_id, last_welcome[chat_id])
            del last_welcome[chat_id]
        except Exception as e:
            logger.debug(f"Could not delete previous welcome message: {e}")

async def schedule_left_message_deletion(client, chat_id, message_id, delay=30):
    """Schedule deletion of left message after delay"""
    if chat_id in left_message_tasks:
        left_message_tasks[chat_id].cancel()

    async def delete_task():  
        try:  
            await asyncio.sleep(delay)  
            await client.delete_messages(chat_id, message_id)  
            if chat_id in left_message_tasks:  
                del left_message_tasks[chat_id]  
        except asyncio.CancelledError:  
            logger.debug(f"Left message deletion task cancelled for chat {chat_id}")  
        except Exception as e:  
            logger.error(f"Error deleting left message: {e}")  
    
    task = asyncio.create_task(delete_task())  
    left_message_tasks[chat_id] = task

@app.on_message(filters.command("welcomestatus") & filters.group)
async def welcome_status(client, message: Message):
    """Show current welcome and left message status"""
    try:
        chat_id = message.chat.id
        welcome_status = "ᴇɴᴀʙʟᴇᴅ" if is_welcome_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"
        left_status = "ᴇɴᴀʙʟᴇᴅ" if is_left_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

        await message.reply_text(  
            f"<b>ᴡᴇʟᴄᴏᴍᴇ sᴛᴀᴛᴜs:</b> {welcome_status}\n"  
            f"<b>ʟᴇғᴛ sᴛᴀᴛᴜs:</b> {left_status}\n"  
            f"<b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat_id}</code>",  
            parse_mode=enums.ParseMode.HTML  
        )  
    except Exception as e:  
        logger.error(f"Error in welcome_status command: {e}")  
        await message.reply_text("❌ <b>An error occurred while fetching status.</b>")

@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(client, message: Message):
    """Handle welcome command"""
    try:
        chat_id = message.chat.id
        chat_title = message.chat.title or "This Group"
        status = "ᴇɴᴀʙʟᴇᴅ" if is_welcome_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

        keyboard = InlineKeyboardMarkup([  
            [  
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data=f"w_on_{chat_id}"),  
                InlineKeyboardButton("❌ ᴅɪsᴀʙʟᴇ", callback_data=f"w_off_{chat_id}")  
            ]  
        ])  

        await message.reply_text(  
            f"<b>🏷 ɢʟᴏᴜᴘ ɴᴀᴍᴇ:</b> <i>{chat_title}</i>\n"  
            f"<b>🆔 ɢʀᴏᴜᴘ ɪᴅ:</b> <code>{chat_id}</code>\n"  
            f"<b>📝 ᴡᴇʟᴄᴏᴍᴇ sᴛᴀᴛᴜs:</b> <b>{status}</b>",  
            reply_markup=keyboard,  
            parse_mode=enums.ParseMode.HTML  
        )  
    except Exception as e:  
        logger.error(f"Error in welcome command: {e}")  
        await message.reply_text("❌ <b>An error occurred while processing the command.</b>")

@app.on_message(filters.command("left") & filters.group)
async def left_cmd(client, message: Message):
    """Handle left command"""
    try:
        chat_id = message.chat.id
        chat_title = message.chat.title or "This Group"
        status = "ᴇɴᴀʙʟᴇᴅ" if is_left_enabled(chat_id) else "ᴅɪsᴀʙʟᴇᴅ"

        keyboard = InlineKeyboardMarkup([  
            [  
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data=f"l_on_{chat_id}"),  
                InlineKeyboardButton("❌ ᴅɪsᴀʙʟᴇ", callback_data=f"l_off_{chat_id}")  
            ]  
        ])  

        await message.reply_text(  
            f"<b>🏷 ɢʀᴏᴜᴘ ɴᴀᴍᴇ:</b> <i>{chat_title}</i>\n"  
            f"<b>🆔 ɢʀᴏᴜᴘ ɪᴅ:</b> <code>{chat_id}</code>\n"  
            f"<b>👋 ʟᴇғᴛ sᴛᴀᴛᴜs:</b> <b>{status}</b>",  
            reply_markup=keyboard,  
            parse_mode=enums.ParseMode.HTML  
        )  
    except Exception as e:  
        logger.error(f"Error in left command: {e}")  
        await message.reply_text("❌ <b>An error occurred while processing the command.</b>")

@app.on_callback_query()
async def callback_toggle(client, callback_query: CallbackQuery):
    """Handle callback queries for toggling welcome/left messages"""
    try:
        user = callback_query.from_user
        data = callback_query.data

        if not data:  
            return  

        parts = data.split("_")  
        if len(parts) < 3:  
            return  
              
        action_type = parts[0]
        action = parts[1]
        chat_id = int(parts[2])  

        if not await is_admin(client, chat_id, user.id):  
            await callback_query.answer(  
                "⚠️ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!",   
                show_alert=True  
            )  
            return  

        chat_title = callback_query.message.chat.title or "This Group"  
        
        if action_type == "w":  
            if action == "on":  
                if not is_welcome_enabled(chat_id):  
                    if set_welcome(chat_id, True):  
                        new_text = f"✅ <b>ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
                    else:  
                        new_text = "❌ <b>Failed to enable welcome messages. Database error.</b>"  
                else:  
                    new_text = f"ℹ️ <b>ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
            else:
                if is_welcome_enabled(chat_id):  
                    if set_welcome(chat_id, False):  
                        new_text = f"❌ <b>ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
                    else:  
                        new_text = "❌ <b>Failed to disable welcome messages. Database error.</b>"  
                else:  
                    new_text = f"ℹ️ <b>ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
        
        elif action_type == "l":  
            if action == "on":  
                if not is_left_enabled(chat_id):  
                    if set_left(chat_id, True):  
                        new_text = f"✅ <b>ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
                    else:  
                        new_text = "❌ <b>Failed to enable left messages. Database error.</b>"  
                else:  
                    new_text = f"ℹ️ <b>ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
            else:
                if is_left_enabled(chat_id):  
                    if set_left(chat_id, False):  
                        new_text = f"❌ <b>ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
                    else:  
                        new_text = "❌ <b>Failed to disable left messages. Database error.</b>"  
                else:  
                    new_text = f"ℹ️ <b>ʟᴇғᴛ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ:</b> <i>{chat_title}</i>"  
        else:  
            return  

        if callback_query.message.text != new_text:  
            await callback_query.message.edit_text(  
                new_text,   
                parse_mode=enums.ParseMode.HTML  
            )  
        
        await callback_query.answer()  

    except ValueError:  
        await callback_query.answer("❌ Invalid callback data!", show_alert=True)  
    except Exception as e:  
        logger.error(f"Error in callback_toggle: {e}")  
        await callback_query.answer("❌ An error occurred!", show_alert=True)

@app.on_chat_member_updated()
async def handle_chat_member_update(client, chat_member: ChatMemberUpdated):
    """Handle chat member updates (joins and leaves)"""
    try:
        chat_id = chat_member.chat.id
        
        if not hasattr(chat_member, 'old_chat_member') or not hasattr(chat_member, 'new_chat_member'):
            logger.info("Null chat member data, skipping...")
            return
            
        old_member = chat_member.old_chat_member
        new_member = chat_member.new_chat_member
        
        if not hasattr(old_member, 'user') or not hasattr(new_member, 'user'):
            logger.info("Missing user data in member update, skipping...")
            return
            
        user = new_member.user or old_member.user
        
        if user.is_bot:
            logger.info(f"Skipping bot user: {user.first_name}")
            return
            
        old_status = old_member.status
        new_status = new_member.status
        
        logger.info(f"Processing: {user.first_name} ({user.id})")
        logger.info(f"Status change: {old_status} -> {new_status}")
        
        join_from_statuses = [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED, None]
        join_to_statuses = [  
            enums.ChatMemberStatus.MEMBER,   
            enums.ChatMemberStatus.ADMINISTRATOR,   
            enums.ChatMemberStatus.OWNER  
        ]
        
        if old_status in join_from_statuses and new_status in join_to_statuses:
            logger.info(f"User {user.first_name} joined chat {chat_id}")
            await handle_user_join(client, chat_id, user)
        
        elif old_status in join_to_statuses and new_status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
            logger.info(f"User {user.first_name} left chat {chat_id}")
            await handle_user_leave(client, chat_id, user)
        else:
            logger.info(f"No action needed for status change: {old_status} -> {new_status}")
                
    except Exception as e:  
        logger.error(f"Error in handle_chat_member_update: {e}")  
        import traceback  
        logger.error(traceback.format_exc())

async def handle_user_join(client, chat_id, user):
    """Handle user joining"""
    try:
        if not is_welcome_enabled(chat_id):
            logger.info(f"Welcome disabled for chat {chat_id}")
            return

        await delete_previous_welcome(client, chat_id)  

        text = random.choice(ShrutiWelcome).format(user=user.mention)  
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)  
        last_welcome[chat_id] = sent.id  
        logger.info(f"Sent welcome message for {user.first_name} in {chat_id}")  
        
    except Exception as e:  
        logger.error(f"Error handling user join: {e}")

async def handle_user_leave(client, chat_id, user):
    """Handle user leaving"""
    try:
        if not is_left_enabled(chat_id):
            logger.info(f"Left messages disabled for chat {chat_id}")
            return

        text = random.choice(ShrutiLeft).format(user=user.mention)  
        sent = await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)  
        logger.info(f"Sent left message for {user.first_name} in {chat_id}")  
        
        await schedule_left_message_deletion(client, chat_id, sent.id)  
        
    except Exception as e:  
        logger.error(f"Error handling user leave: {e}")



@app.on_message(filters.new_chat_members & filters.group)
async def handle_new_members(client, message: Message):
    """Handle new chat members (alternative approach)"""
    try:
        chat_id = message.chat.id

        if not is_welcome_enabled(chat_id):  
            logger.info(f"Welcome disabled for chat {chat_id}")  
            return  
        
        await delete_previous_welcome(client, chat_id)  
        
        for user in message.new_chat_members:  
            if user.is_bot:  
                logger.info(f"Skipping bot user: {user.first_name}")  
                continue  
                
            logger.info(f"New member detected: {user.first_name} in chat {chat_id}")  
            
            text = random.choice(ShrutiWelcome).format(user=user.mention)  
            sent = await message.reply_text(text, parse_mode=enums.ParseMode.HTML)  
            last_welcome[chat_id] = sent.id  
            logger.info(f"Sent welcome message for {user.first_name}")  
            
    except Exception as e:  
        logger.error(f"Error in handle_new_members: {e}")

@app.on_message(filters.left_chat_member & filters.group)
async def handle_left_member(client, message: Message):
    """Handle left chat member (alternative approach)"""
    try:
        chat_id = message.chat.id
        user = message.left_chat_member

        if not user or user.is_bot:  
            return  
            
        if not is_left_enabled(chat_id):  
            logger.info(f"Left messages disabled for chat {chat_id}")  
            return  
        
        logger.info(f"Member left detected: {user.first_name} from chat {chat_id}")  
        
        text = random.choice(ShrutiLeft).format(user=user.mention)  
        sent = await message.reply_text(text, parse_mode=enums.ParseMode.HTML)  
        logger.info(f"Sent left message for {user.first_name}")  
        
        await schedule_left_message_deletion(client, chat_id, sent.id)  
        
    except Exception as e:  
        logger.error(f"Error in handle_left_member: {e}")


logger.info("Welcome/Left module loaded successfully!")
