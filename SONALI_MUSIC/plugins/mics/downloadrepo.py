from pyrogram import Client, filters
import git
import shutil
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from SONALI_MUSIC import app

# Create a thread pool executor for blocking operations
executor = ThreadPoolExecutor(max_workers=3)

@app.on_message(filters.command(["downloadrepo"]))
async def download_repo(_, message):
    if len(message.command) != 2:
        await message.reply_text("**⋟ ᴘʀᴏᴠɪᴅᴇ ɢɪᴛʜᴜʙ ʀᴇᴘᴏ ᴜʀʟ ᴀꜰᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**\n\n**ᴇxᴀᴍᴘʟᴇ :-** `/downloadrepo Repo url`")
        return

    repo_url = message.command[1]
    status_msg = await message.reply_text("**⋟ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀɴᴅ ᴢɪᴘᴘɪɴɢ ᴛʜᴇ ʀᴇᴘᴏꜱɪᴛᴏʀʏ, ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...**")
    
    try:
        # Run the blocking operation in a separate thread
        loop = asyncio.get_event_loop()
        zip_path = await loop.run_in_executor(executor, download_and_zip_repo, repo_url)
        
        if zip_path and os.path.exists(zip_path):
            await message.reply_document(zip_path, caption=f"**⋟ ʀᴇᴘᴏꜱɪᴛᴏʀʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!**\n\n**ʀᴇᴘᴏ:** `{repo_url}`")
            await status_msg.delete()
        else:
            await message.reply_text("**⋟ ᴜɴᴀʙʟᴇ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ꜱᴘᴇᴄɪꜰɪᴇᴅ ɢɪᴛʜᴜʙ ʀᴇᴘᴏꜱɪᴛᴏʀʏ.**")
    except Exception as e:
        await message.reply_text(f"**⋟ ᴇʀʀᴏʀ: {e}**")
    finally:
        # Clean up
        if 'zip_path' in locals() and zip_path and os.path.exists(zip_path):
            os.remove(zip_path)

def download_and_zip_repo(repo_url):
    repo_path = ""
    try:
        # Extract repo name from URL
        if repo_url.endswith('.git'):
            repo_name = repo_url.split('/')[-1][:-4]
        else:
            repo_name = repo_url.split('/')[-1]
        
        repo_path = f"temp_{repo_name}"
        
        # Clone the repository
        print(f"Cloning repository: {repo_url}")
        git.Repo.clone_from(repo_url, repo_path, depth=1)
        
        # Create a zip archive
        print(f"Creating zip archive for: {repo_path}")
        zip_filename = shutil.make_archive(repo_name, 'zip', repo_path)
        print(f"Zip created: {zip_filename}")
        
        return zip_filename
        
    except git.exc.GitCommandError as e:
        print(f"Git error: {e}")
        return None
    except Exception as e:
        print(f"Error downloading and zipping GitHub repository: {e}")
        return None
    finally:
        # Clean up the cloned repository
        if repo_path and os.path.exists(repo_path):
            print(f"Cleaning up: {repo_path}")
            shutil.rmtree(repo_path, ignore_errors=True)
