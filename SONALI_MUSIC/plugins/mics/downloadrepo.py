from pyrogram import Client, filters
import git
import shutil
import os
import asyncio
from SONALI_MUSIC import app

@app.on_message(filters.command(["downloadrepo"]))
async def download_repo(_, message):
    if len(message.command) != 2:
        await message.reply_text("**⋟ ᴘʀᴏᴠɪᴅᴇ ɢɪᴛʜᴜʙ ʀᴇᴘᴏ ᴜʀʟ ᴀꜰᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**\n\n**ᴇxᴀᴍᴘʟᴇ :-** `/downloadrepo Repo url`")
        return

    repo_url = message.command[1]
    await message.reply_text("**⋟ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀɴᴅ ᴢɪᴘᴘɪɴɢ ᴛʜᴇ ʀᴇᴘᴏꜱɪᴛᴏʀʏ, ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...**")
    
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, download_and_send, message, repo_url)

def download_and_send(message, repo_url):
    zip_path = download_and_zip_repo(repo_url)
    if zip_path:
        try:
        
            with open(zip_path, "rb") as zip_file:
                
                asyncio.run_coroutine_threadsafe(
                    message.reply_document(zip_file), 
                    asyncio.get_event_loop()
                ).result()
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                message.reply_text(f"⋟ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇɴᴅ ᴢɪᴘ: {e}"),
                asyncio.get_event_loop()
            ).result()
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)
    else:
        asyncio.run_coroutine_threadsafe(
            message.reply_text("**⋟ ᴜɴᴀʙʟᴇ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ꜱᴘᴇᴄɪꜰɪᴇᴅ ɢɪᴛʜᴜʙ ʀᴇᴘᴏꜱɪᴛᴏʀʏ.**"),
            asyncio.get_event_loop()
        ).result()

def download_and_zip_repo(repo_url):
    try:
        repo_name = os.path.splitext(repo_url.split("/")[-1])[0]
        repo_path = f"{repo_name}"
        
    
        git.Repo.clone_from(repo_url, repo_path)
        
    
        shutil.make_archive(repo_path, 'zip', repo_path)
        return f"{repo_path}.zip"
    except Exception as e:
        print(f"**⋟ ᴇʀʀᴏʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀɴᴅ ᴢɪᴘᴘɪɴɢ ɢɪᴛʜᴜʙ ʀᴇᴘᴏꜱɪᴛᴏʀʏ :-** {e}")
        return None
    finally:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
