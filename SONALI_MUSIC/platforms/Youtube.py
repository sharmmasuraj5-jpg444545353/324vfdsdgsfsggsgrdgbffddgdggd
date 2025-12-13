<<<<<<< Current (Your changes)
=======
# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀

# This source code is under MIT License 📜 Unauthorized forking, importing, or using this code without giving proper credit will result in legal action ⚠️
 
# 📩 DM for permission : @brahix
# =======================================================


import asyncio
import os
import re
import json
import time
from typing import Union
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from SONALI_MUSIC.utils.database import is_on_off
from SONALI_MUSIC.utils.formatters import time_to_seconds
import os
import glob
import random
import logging
import aiohttp
# Note: Configuration below is isolated in Youtube.py and NOT connected to config.py
# This ensures independent operation of the channel caching system
import config
#from config import API_URL, VIDEO_API_URL, API_KEY
from os import getenv
from motor.motor_asyncio import AsyncIOMotorClient
from SONALI_MUSIC import app

# === HARDCODED CONFIGURATION ===
AUDIO_CHANNEL_ID = int("-1003472388712")
VIDEO_CHANNEL_ID = int("-1003365514903")
BOT_TOKEN = "8208037536:AAEXcEDC4__HJ63Vx7puXSUVswNv6wuhH0I"
OWNER_ID = int("8115787127")
MONGODB_URI = "mongodb+srv://sandeep:fpA5BAT3VqCq0THj@cluster0.bege5a8.mongodb.net/destinymusic?retryWrites=true&w=majority&appName=Cluster0"
YOUTUBE_API_KEY = "AIzaSyDcJYgflcDs4vmrx8rlEjNdnwJQPds_978"

API_URL = getenv("API_URL", 'https://api.thequickearn.xyz')
API_KEY = getenv("API_KEY", 'NxGBNexGenBotsa02f5a')
VIDEO_API_URL = getenv("VIDEO_API_URL", 'https://api.video.thequickearn.xyz')

# === SEPARATE BOT FOR CHANNEL OPERATIONS ===
try:
    from pyrogram import Client
    # Create separate bot client for channel operations
    channel_bot = Client(
        name="ChannelCacheBot",
        api_id=6,  # Using default API ID
        api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",  # Using default API hash
        bot_token=BOT_TOKEN,
        no_updates=True  # Don't receive updates, only used for uploading
    )
    print("✅ Channel bot client created")
except Exception as e:
    print(f"⚠️ Failed to create channel bot: {e}")
    channel_bot = None

# === MONGODB CONNECTION ===
try:
    mongo_client = AsyncIOMotorClient(MONGODB_URI)
    mongodb = mongo_client.destinymusic
    songs_db = mongodb.songs_cache
    print("✅ Connected to MongoDB for songs cache")
except Exception as e:
    print(f"⚠️ MongoDB connection error: {e}")
    songs_db = None

# === SAAVN API CONFIGURATION ===
SAVN_API_BASE = "https://apikeyy-zeta.vercel.app/api/search"
SAVN_SONGS_API = "https://apikeyy-zeta.vercel.app/api/songs"

# === CHANNEL CACHE FUNCTIONS ===
async def get_song_hash(query: str, is_video: bool = False):
    """Generate a hash for the song query"""
    import hashlib
    query_lower = query.lower().strip()
    query_hash = hashlib.md5(f"{query_lower}_{'video' if is_video else 'audio'}".encode()).hexdigest()
    return query_hash

async def check_channel_cache(query: str, video_id: str = None, is_video: bool = False):
    """Check if song exists in MongoDB and Telegram channel, download and return file path"""
    try:
        if songs_db is None:
            return None
        
        # Use video_id/audio_id for caching instead of query hash
        if video_id:
            cache_key = video_id
            search_field = "video_id" if is_video else "audio_id"
        else:
            # Fallback to query hash if no video_id provided
            cache_key = await get_song_hash(query, is_video)
            search_field = "query_hash"
        
        # Check MongoDB
        song_data = await songs_db.find_one({search_field: cache_key})
        
        if song_data:
            message_id = song_data.get("message_id")
            channel_id = song_data.get("channel_id")
            
            if message_id and channel_id:
                try:
                    # Try to get the message from channel
                    message = await channel_bot.get_messages(channel_id, message_id)
                    if message:
                        # Download the file to local path
                        download_folder = "downloads"
                        os.makedirs(download_folder, exist_ok=True)
                        
                        # Get file based on type
                        file_to_download = None
                        file_extension = None
                        
                        if is_video:
                            if message.video:
                                file_to_download = message.video
                                file_extension = "mp4"
                            elif message.document:
                                file_to_download = message.document
                                file_extension = message.document.file_name.split('.')[-1] if message.document.file_name else "mp4"
                        else:
                            if message.audio:
                                file_to_download = message.audio
                                file_extension = message.audio.file_name.split('.')[-1] if message.audio.file_name else "mp3"
                            elif message.voice:
                                file_to_download = message.voice
                                file_extension = "ogg"
                            elif message.document:
                                file_to_download = message.document
                                file_extension = message.document.file_name.split('.')[-1] if message.document.file_name else "mp3"
                        
                        if file_to_download:
                            # Create unique file path using video_id or cache_key
                            file_name = video_id if video_id else cache_key
                            file_path = os.path.join(download_folder, f"{file_name}.{file_extension}")
                            
                            # Check if file already exists
                            if os.path.exists(file_path):
                                print(f"✅ File already exists in cache: {file_path}")
                                return file_path
                            
                            # Download the file
                            print(f"📥 Downloading from channel cache: {query}")
                            await app.download_media(message, file_name=file_path)
                            
                            if os.path.exists(file_path):
                                print(f"✅ Downloaded from channel cache: {file_path}")
                                return file_path
                            
                except Exception as e:
                    print(f"⚠️ Error getting/downloading message from channel: {e}")
                    import traceback
                    traceback.print_exc()
                    # Message might be deleted, remove from DB
                    try:
                        await songs_db.delete_one({search_field: cache_key})
                    except:
                        pass
        
        return None
    except Exception as e:
        print(f"⚠️ Error checking channel cache: {e}")
        import traceback
        traceback.print_exc()
        return None

async def verify_channel_access(channel_id: int):
    """Verify if channel bot can access the channel"""
    try:
        if channel_bot is None:
            print("⚠️ Channel bot not available for verification")
            return False, None

        channel_info = await channel_bot.get_chat(channel_id)
        # Try to get bot's member status
        try:
            bot_member = await channel_bot.get_chat_member(channel_id, channel_bot.me.id)
            print(f"✅ Channel bot is member of channel: {channel_info.title} (Status: {bot_member.status})")
            return True, channel_info
        except Exception as e:
            print(f"⚠️ Channel bot is not a member of channel {channel_id}: {e}")
            return False, channel_info
    except Exception as e:
        print(f"⚠️ Channel bot cannot access channel {channel_id}: {e}")
        return False, None

async def save_to_channel_cache(query: str, file_path: str, video_id: str = None, is_video: bool = False):
    """Upload file to channel and save to MongoDB"""
    try:
        if songs_db is None:
            print("⚠️ MongoDB not connected, cannot save to cache")
            return None
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            return None
            
        channel_id = VIDEO_CHANNEL_ID if is_video else AUDIO_CHANNEL_ID
        
        # Use video_id/audio_id for caching instead of query hash
        if video_id:
            cache_key = video_id
            search_field = "video_id" if is_video else "audio_id"
        else:
            # Fallback to query hash if no video_id provided
            cache_key = await get_song_hash(query, is_video)
            search_field = "query_hash"
        
        print(f"📤 Uploading to channel {channel_id}: {query} (File: {file_path})")
        
        # First, verify bot can access the channel
        can_access, channel_info = await verify_channel_access(channel_id)
        if not can_access:
            print(f"⚠️ Channel bot cannot access channel {channel_id}")
            print(f"⚠️ To fix: Add channel bot to channel as admin with 'Post Messages' permission")
            print(f"⚠️ Skipping upload but file is ready for playback")
            # Return file path even if upload fails, so song can still play
            return file_path

        # Upload to channel using separate channel bot
        try:
            if channel_bot is None:
                print("⚠️ Channel bot not available, skipping upload")
                return file_path

            if is_video:
                message = await channel_bot.send_video(
                    chat_id=channel_id,
                    video=file_path,
                    caption=f"🎵 {query}\n#Cached"
                )
            else:
                message = await channel_bot.send_audio(
                    chat_id=channel_id,
                    audio=file_path,
                    caption=f"🎵 {query}\n#Cached"
                )
            
            if not message:
                print(f"⚠️ Failed to upload: Message is None")
                # Return file path so song can still play
                return file_path
                
            message_id = message.id
            print(f"✅ Uploaded to channel: Message ID {message_id}")
            
            # Get file_id - refresh message to get updated file_id
            try:
                message = await channel_bot.get_messages(channel_id, message_id)
                if is_video:
                    file_id = message.video.file_id if message.video else (message.document.file_id if message.document else None)
                else:
                    file_id = message.audio.file_id if message.audio else (message.voice.file_id if message.voice else (message.document.file_id if message.document else None))
            except Exception as e:
                print(f"⚠️ Could not get file_id: {e}")
                file_id = None
            
            if message_id:
                # Save to MongoDB - ONLY store video_id/audio_id, message_id, and channel_id
                if songs_db is not None:
                    # Minimal data structure - only what's needed for playback
                    update_data = {
                        "message_id": message_id,
                        "channel_id": channel_id,
                    }
                    # Add the appropriate ID field (video_id or audio_id)
                    if video_id:
                        if is_video:
                            update_data["video_id"] = video_id
                        else:
                            update_data["audio_id"] = video_id
                    else:
                        # Fallback: use query_hash if no video_id available
                        update_data["query_hash"] = cache_key
                    
                    try:
                        await songs_db.update_one(
                            {search_field: cache_key},
                            {"$set": update_data},
                            upsert=True
                        )
                        print(f"✅ Saved to MongoDB cache: {query} (ID: {cache_key}, Message ID: {message_id}, Channel: {channel_id})")
                        return file_id if file_id else message_id
                    except Exception as e:
                        print(f"⚠️ Error saving to MongoDB: {e}")
                        import traceback
                        traceback.print_exc()
                        return None
            else:
                print(f"⚠️ No message_id received after upload")
                return None
            
        except Exception as e:
            error_msg = str(e)
            if "CHANNEL_INVALID" in error_msg or "ChannelInvalid" in error_msg:
                print(f"⚠️ Channel {channel_id} is invalid or bot is not a member")
                print(f"⚠️ Please add the bot to the channel as admin. Skipping upload but file is ready.")
            elif "CHAT_ADMIN_REQUIRED" in error_msg or "ChatAdminRequired" in error_msg:
                print(f"⚠️ Bot needs admin rights in channel {channel_id}")
                print(f"⚠️ Skipping upload but file is ready.")
            else:
                print(f"⚠️ Error uploading to channel: {e}")
                import traceback
                traceback.print_exc()
            # Return file path even if upload fails, so song can still play
            return file_path
        
        return None
    except Exception as e:
        print(f"⚠️ Error saving to channel cache: {e}")
        import traceback
        traceback.print_exc()
        return None

async def get_channel_file(file_id: str):
    """Get file path from Telegram file_id"""
    try:
        # For Telegram files, we can use the file_id directly
        # The file_id can be used in stream() function
        return file_id
    except Exception as e:
        print(f"⚠️ Error getting channel file: {e}")
        return None

def cookie_txt_file():
    """Get a random cookie file from the cookies directory"""
    try:
        cookie_dir = f"{os.getcwd()}/cookies"
        
        # Check if cookies directory exists
        if not os.path.exists(cookie_dir):
            print(f"⚠️ Cookies directory not found: {cookie_dir}")
            # Try to create hardcoded cookie file
            return create_hardcoded_cookie_file()
        
        # Get all .txt files in cookies directory
        txt_files = glob.glob(os.path.join(cookie_dir, '*.txt'))
        
        if not txt_files:
            print(f"⚠️ No .txt files found in cookies directory")
            # Try to create hardcoded cookie file
            return create_hardcoded_cookie_file()
        
        # Randomly select a cookie file
        cookie_file = random.choice(txt_files)
        
        # Log the chosen file
        log_file = os.path.join(cookie_dir, "logs.csv")
        try:
            with open(log_file, 'a', encoding='utf-8') as file:
                file.write(f'Choosen File : {cookie_file}\n')
        except Exception as e:
            print(f"Could not write to log file: {e}")
        
        print(f"🍪 Using cookie file: {cookie_file}")
        return cookie_file
        
    except Exception as e:
        print(f"⚠️ Error getting cookie file: {e}")
        # Fallback to hardcoded cookies
        return create_hardcoded_cookie_file()

def create_hardcoded_cookie_file():
    """Create a hardcoded cookie file when no external cookies are found"""
    try:
        # Hardcoded YouTube cookies for better quality downloads
        cookie_content = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1770704847	LOGIN_INFO	AFmmF2swRQIgNGkDUBtCGpbyrghQT0tWFpfMQPS9KCEUpPODMlPNIWwCIQC2CBWceu81MCBsWB4Baw1pf3SqA_5D22GW3jbouhSGZA:QUQ3MjNmemtob3JkZ05YZ2lrUGpIbVBwRXk2ZHFrb0VtRzdIZ2tmaHFqeUZBeGxBdko5MzZvT0lCWXZkbFZwd0RyNkVqb1d6WVVkb0sxdFRUWEZhX0h2dTlfUHlXN2hkVElINzdhMEk2TUNGWnNMNDdCRnQ5WGU5ZWZXazhwOUJTMHpQYmVkRmpacy1UTk0yc2xtZFRBUGFCM2JTNi1hSzZB
.youtube.com	TRUE	/	TRUE	1781160556	PREF	f4=4000000&tz=Asia.Calcutta&f7=100
.youtube.com	TRUE	/	FALSE	1779360012	SID	g.a0003wjx1OxwERsi_jbYPTIgq4HWJZWqSvbIgLzwU6GALLBWI7sOIV4WHWrMyrhBGGVIaxPaqQACgYKAWISARESFQHGX2MiAhyUvJjR4x9yVvq6Nj9D2BoVAUF8yKqnAtflZguLc0drrBiCNZD-0076
.youtube.com	TRUE	/	TRUE	1779360012	__Secure-1PSID	g.a0003wjx1OxwERsi_jbYPTIgq4HWJZWqSvbIgLzwU6GALLBWI7sO1aXec3YHL17L_XxHS8KFeQACgYKAUASARESFQHGX2Mi2NGsBkJi3Nk2Yi1rfEHh8BoVAUF8yKot0caG26LpEjagNX1V6mjD0076
.youtube.com	TRUE	/	TRUE	1779360012	__Secure-3PSID	g.a0003wjx1OxwERsi_jbYPTIgq4HWJZWqSvbIgLzwU6GALLBWI7sO4-dinAqQInep8HXKTn1RrAACgYKASMSARESFQHGX2MiBRQO7NU5IsFh3ibcSGMBGRoVAUF8yKp5SyVc86pe_33LJF1xDdmU0076
.youtube.com	TRUE	/	FALSE	1779360012	HSID	AZ6Ss-N5G7ikI8GJG
.youtube.com	TRUE	/	TRUE	1779360012	SSID	ANr7N4jTducFotrlc
.youtube.com	TRUE	/	FALSE	1779360012	APISID	E8SWJGBv2CN8NCd7/AWI75uMLfeTuF5AO3
.youtube.com	TRUE	/	TRUE	1779360012	SAPISID	BSwotq3K_osWdRba/AJ07-3YcjI9m_ZicB
.youtube.com	TRUE	/	TRUE	1779360012	__Secure-1PAPISID	BSwotq3K_osWdRba/AJ07-3YcjI9m_ZicB
.youtube.com	TRUE	/	TRUE	1779360012	__Secure-3PAPISID	BSwotq3K_osWdRba/AJ07-3YcjI9m_ZicB
.youtube.com	TRUE	/	TRUE	0	wide	1
.youtube.com	TRUE	/	TRUE	1781165605	__Secure-1PSIDTS	sidts-CjQBflaCdXU8P1eZMPGMOzy-PL5tlPaf9s1H4lCYc3eINvNfnp5-NYWLEHwHnqcrQRqVMYKeEAA
.youtube.com	TRUE	/	TRUE	1781165605	__Secure-3PSIDTS	sidts-CjQBflaCdXU8P1eZMPGMOzy-PL5tlPaf9s1H4lCYc3eINvNfnp5-NYWLEHwHnqcrQRqVMYKeEAA
.youtube.com	TRUE	/	FALSE	1781165605	SIDCC	AKEyXzXo4VKm0B4TmsTpBT-AdXb6oH-VKFHsJIucIeFAMaud9dwvZ3SKjQQQ4M9_m3dio8idMIA
.youtube.com	TRUE	/	TRUE	1781165605	__Secure-1PSIDCC	AKEyXzXgjlVV98S2YvN0If8j4ibOBCCnXvSy1WKApeyHLzpL7lp74GzqhsJFfz-cTGQmBUNB7A
.youtube.com	TRUE	/	TRUE	1781165605	__Secure-3PSIDCC	AKEyXzXtrLYTAWwxjK41uhIiXAFouNCYzhH4h-87rnXDNHv8wtScX4e_zyKjK0RFN2IyK9oMO30
.youtube.com	TRUE	/	TRUE	1781160562	VISITOR_INFO1_LIVE	bm_Jiq98kyw
.youtube.com	TRUE	/	TRUE	1781160562	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgTA%3D%3D
.youtube.com	TRUE	/	TRUE	1781095671	__Secure-ROLLOUT_TOKEN	CO_2k4e6_-LopgEQ6dPNo5bzigMYs4y024q4kQM%3D
.youtube.com	TRUE	/	TRUE	0	YSC	fePyUxJCWXI"""
        
        # Create cookies directory if it doesn't exist
        cookie_dir = f"{os.getcwd()}/cookies"
        os.makedirs(cookie_dir, exist_ok=True)
        
        # Save hardcoded cookies to file
        cookie_file_path = os.path.join(cookie_dir, "hardcoded_cookies.txt")
        with open(cookie_file_path, 'w', encoding='utf-8') as f:
            f.write(cookie_content)
        
        print(f"🍪 Created hardcoded cookie file: {cookie_file_path}")
        return cookie_file_path
        
    except Exception as e:
        print(f"⚠️ Error creating hardcoded cookie file: {e}")
        return None

# === SAAVN API FUNCTIONS ===
def clean_query(query: str):
    """Clean and optimize search query for better Saavn matching"""
    # Remove common words that might interfere with search
    stop_words = ['song', 'music', 'video', 'official', 'lyrics', 'hd', '4k', 'full', 'ft', 'feat', 'featuring']
    query = query.lower().strip()
    
    # Remove hashtags and special characters first
    query = re.sub(r'#', '', query)
    query = re.sub(r'\|', ' ', query)
    
    # Remove stop words
    words = query.split()
    cleaned_words = [word for word in words if word not in stop_words]
    
    # Join back and clean
    cleaned_query = ' '.join(cleaned_words)
    
    # Remove extra spaces and special characters but keep Hindi/Unicode characters
    cleaned_query = re.sub(r'[^\w\s\u0900-\u097F]', '', cleaned_query)  # Keep Hindi characters
    cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
    
    return cleaned_query

def generate_saavn_search_variations(query: str):
    """Generate multiple search variations for better Saavn matching"""
    variations = []
    
    # Original query
    variations.append(query)
    
    # Cleaned query
    cleaned = clean_query(query)
    if cleaned != query.lower():
        variations.append(cleaned)
    
    # Extract main song title (before | or -)
    if '|' in query:
        main_title = query.split('|')[0].strip()
        variations.append(main_title)
        variations.append(clean_query(main_title))
    
    if '-' in query:
        main_title = query.split('-')[0].strip()
        variations.append(main_title)
        variations.append(clean_query(main_title))
    
    # Try with just first few words
    words = query.split()
    if len(words) > 3:
        variations.append(' '.join(words[:3]))
        variations.append(' '.join(words[:2]))
    
    # Try with Hindi words only
    hindi_words = [word for word in words if re.search(r'[\u0900-\u097F]', word)]
    if hindi_words:
        variations.append(' '.join(hindi_words))
    
    # Try with English words only
    english_words = [word for word in words if not re.search(r'[\u0900-\u097F]', word) and word.isalpha()]
    if english_words:
        variations.append(' '.join(english_words))
    
    # Remove duplicates and empty strings
    variations = list(dict.fromkeys([v for v in variations if v.strip()]))
    
    return variations

def find_best_match(songs: list, original_query: str):
    """Find the best matching song from search results with improved matching"""
    if not songs:
        return None
        
    original_query = original_query.lower().strip()
    cleaned_query = clean_query(original_query)
    
    # Extract key words from the query (first 2-3 words)
    query_words = cleaned_query.split()[:3]  # Only use first 3 words
    
    # Score each song based on title similarity
    scored_songs = []
    
    for song in songs:
        title = song.get("title", "").lower()
        artist = song.get("primaryArtists", "").lower()
        
        # Calculate similarity score
        score = 0
        
        # Exact title match gets highest score
        if cleaned_query in title:
            score += 100
            
        # Check if all query words are in the title
        title_words = title.split()
        matching_words = sum(1 for word in query_words if word in title_words)
        
        # If most query words match, give high score
        if matching_words >= len(query_words) * 0.7:  # 70% of words match
            score += 80
        
        # Partial word matching
        score += matching_words * 15
        
        # Exact word order match bonus
        if len(query_words) >= 2:
            # Check if first two words appear in order
            if query_words[0] in title and query_words[1] in title:
                if title.find(query_words[0]) < title.find(query_words[1]):
                    score += 30
        
        # Artist match bonus (but not too high to avoid wrong matches)
        if any(word in artist for word in query_words):
            score += 10
            
        # Length similarity bonus (prefer similar length titles)
        length_diff = abs(len(cleaned_query) - len(title))
        if length_diff < 15:
            score += 10
        elif length_diff > 30:  # Penalize very different lengths
            score -= 20
            
        # Penalize if title contains too many extra words
        if len(title_words) > len(query_words) * 2:
            score -= 15
            
        scored_songs.append((score, song))
    
    # Sort by score and return best match
    scored_songs.sort(key=lambda x: x[0], reverse=True)
    
    # Only return if we have a reasonable match (score > 20)
    if scored_songs and scored_songs[0][0] > 20:
        return scored_songs[0][1]
    
    # If no good match found, return None instead of first song
    return None

async def search_saavn_song(query: str):
    """Search for songs using Saavn API with multiple strategies"""
    try:
        # Strategy 1: Original query
        print(f"🔍 Searching Saavn with original query: {query}")
        response = requests.get(SAVN_API_BASE, params={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                songs = []
                if "songs" in data["data"] and "results" in data["data"]["songs"]:
                    songs = data["data"]["songs"]["results"]
                elif "topQuery" in data["data"] and "results" in data["data"]["topQuery"]:
                    songs = data["data"]["topQuery"]["results"]
                elif isinstance(data["data"], list):
                    songs = data["data"]
                
                if songs:
                    best_match = find_best_match(songs, query)
                    if best_match:
                        print(f"✅ Found match with original query: {best_match.get('title')}")
                        return [best_match]
        
        # Strategy 2: Cleaned query
        cleaned_query = clean_query(query)
        if cleaned_query != query.lower():
            print(f"🔍 Trying cleaned query: {cleaned_query}")
            response = requests.get(SAVN_API_BASE, params={"query": cleaned_query})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    songs = []
                    if "songs" in data["data"] and "results" in data["data"]["songs"]:
                        songs = data["data"]["songs"]["results"]
                    elif "topQuery" in data["data"] and "results" in data["data"]["topQuery"]:
                        songs = data["data"]["topQuery"]["results"]
                    elif isinstance(data["data"], list):
                        songs = data["data"]
                    
                    if songs:
                        best_match = find_best_match(songs, query)
                        if best_match:
                            print(f"✅ Found match with cleaned query: {best_match.get('title')}")
                            return [best_match]
        
        # Strategy 3: Try with enhanced variations
        query_variations = generate_saavn_search_variations(query)
        print(f"🔍 Generated {len(query_variations)} search variations")
        
        for i, variation in enumerate(query_variations, 1):
            if variation != query and variation != cleaned_query:
                print(f"🔍 Trying variation {i}: {variation}")
                response = requests.get(SAVN_API_BASE, params={"query": variation})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        songs = []
                        if "songs" in data["data"] and "results" in data["data"]["songs"]:
                            songs = data["data"]["songs"]["results"]
                        elif "topQuery" in data["data"] and "results" in data["data"]["topQuery"]:
                            songs = data["data"]["topQuery"]["results"]
                        elif isinstance(data["data"], list):
                            songs = data["data"]
                        
                        if songs:
                            best_match = find_best_match(songs, query)
                            if best_match:
                                print(f"✅ Found match with variation '{variation}': {best_match.get('title')}")
                                return [best_match]
        
        print(f"❌ No matches found for query: {query}")
        return None
        
    except Exception as e:
        print(f"Saavn search error: {e}")
        return None

async def get_saavn_download_url(song_id: str, song_url: str):
    """Get download URL for Saavn song"""
    try:
        response = requests.get(SAVN_SONGS_API, params={"ids": song_id, "link": song_url})
        print(f"Saavn Songs API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        print(f"Saavn Songs API Data: {data}")
        
        if data.get("success") and "data" in data and len(data["data"]) > 0:
            song_details = data["data"][0]
            download_urls = song_details.get("downloadUrl", [])
            
            # Get the highest quality download URL (320kbps)
            if download_urls and isinstance(download_urls, list):
                for url_info in reversed(download_urls):  # Start from highest quality
                    if isinstance(url_info, dict) and 'url' in url_info:
                        return url_info['url']
                        
        return None
        
    except Exception as e:
        print(f"Saavn download URL error: {e}")
        return None

async def download_with_cookies(link: str, cookie_file: str):
    """
    Download song using yt-dlp with cookies for better quality and access
    """
    try:
        print(f"🍪 Downloading with cookies: {link}")
        
        # Check if cookie file exists
        if not cookie_file or not os.path.exists(cookie_file):
            print(f"⚠️ Cookie file not found: {cookie_file}")
            return None
        
        # Extract video ID for file naming
        try:
            video_id = link.split('v=')[-1].split('&')[0]
        except Exception as e:
            print(f"⚠️ Error extracting video ID: {e}")
            return None
        
        # Check if file already exists
        download_folder = "downloads"
        os.makedirs(download_folder, exist_ok=True)
        
        for ext in ["mp3", "m4a", "webm", "opus"]:
            file_path = f"{download_folder}/{video_id}.{ext}"
            if os.path.exists(file_path):
                print(f"📁 File already exists: {file_path}")
                return file_path
        
        # Use yt-dlp with cookies
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{download_folder}/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "cookiefile": cookie_file,
            "no_warnings": True,
            "extract_flat": False,
        }
        
        loop = asyncio.get_running_loop()
        
        def _download():
            try:
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                # Extract info first
                info = ydl.extract_info(link, download=False)
                if not info:
                    print("❌ Could not extract video info")
                    return None
                
                # Download the file
                ydl.download([link])
                
                # Find the downloaded file
                info_id = info.get('id', video_id)
                info_ext = info.get('ext', 'mp3')
                return os.path.join(download_folder, f"{info_id}.{info_ext}")
            except Exception as e:
                print(f"❌ Download error: {e}")
                return None
        
        downloaded_file = await loop.run_in_executor(None, _download)
        
        if downloaded_file and os.path.exists(downloaded_file):
            print(f"✅ Successfully downloaded with cookies: {downloaded_file}")
            return downloaded_file
        
        print("❌ Downloaded file not found")
        return None
        
    except Exception as e:
        print(f"❌ Cookies download error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def download_saavn_song(query: str):
    """Download song from Saavn API with enhanced matching"""
    try:
        print(f"🎵 Starting Saavn download for: {query}")
        
        # Search for the song with multiple strategies
        songs = await search_saavn_song(query)
        if not songs:
            print(f"❌ No songs found for query: {query}")
            return None, None
            
        song = songs[0]
        title = song.get("title", "Unknown Title")
        artist = song.get("primaryArtists", "Unknown Artist")
        song_id = song.get("id")
        song_url = song.get("url")
        
        print(f"📀 Selected song: {title} by {artist}")
        print(f"🆔 Song ID: {song_id}")
        
        if not song_id:
            print("❌ No song ID found")
            return None, None
            
        # Get download URL
        print(f"🔗 Getting download URL for song ID: {song_id}")
        download_url = await get_saavn_download_url(song_id, song_url)
        
        if not download_url:
            print("❌ Failed to get download URL")
            return None, None
            
        print(f"✅ Successfully got download URL: {download_url[:50]}...")
        return download_url, {
            "title": title,
            "artist": artist,
            "source": "Saavn",
            "quality": "320kbps",
            "song_id": song_id
        }
        
    except Exception as e:
        print(f"❌ Saavn download error: {e}")
        return None, None

async def download_song(link: str):
    try:
        video_id = link.split('v=')[-1].split('&')[0]
    except Exception as e:
        print(f"⚠️ Error extracting video ID from link: {e}")
        return None

    download_folder = "downloads"
    # Ensure download folder exists
    try:
        os.makedirs(download_folder, exist_ok=True)
    except Exception as e:
        print(f"⚠️ Error creating download folder: {e}")
        return None
    
    # Check for existing files
    for ext in ["mp3", "m4a", "webm"]:
        file_path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(file_path):
            print(f"📁 File already exists: {file_path}")
            return file_path
        
    song_url = f"{API_URL}/song/{video_id}?api={API_KEY}"
    async with aiohttp.ClientSession() as session:
        for attempt in range(10):
            try:
                async with session.get(song_url) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status code {response.status}")
                
                    data = await response.json()
                    status = data.get("status", "").lower()

                    if status == "done":
                        download_url = data.get("link")
                        if not download_url:
                            raise Exception("API response did not provide a download URL.")
                        break
                    elif status == "downloading":
                        await asyncio.sleep(4)
                    else:
                        error_msg = data.get("error") or data.get("message") or f"Unexpected status '{status}'"
                        raise Exception(f"API error: {error_msg}")
            except Exception as e:
                print(f"[FAIL] {e}")
                return None
        else:
            print("⏱️ Max retries reached. Still downloading...")
            return None
        
        try:
            file_format = data.get("format", "mp3")
            file_extension = file_format.lower()
            file_name = f"{video_id}.{file_extension}"
            download_folder = "downloads"
            
            # Ensure download folder exists
            try:
                os.makedirs(download_folder, exist_ok=True)
            except Exception as e:
                print(f"⚠️ Error creating download folder: {e}")
                return None
                
            file_path = os.path.join(download_folder, file_name)

            async with session.get(download_url) as file_response:
                if file_response.status != 200:
                    print(f"⚠️ Download failed with status: {file_response.status}")
                    return None
                    
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await file_response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                
                # Verify file was created and has content
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    print(f"✅ Successfully downloaded: {file_path}")
                    return file_path
                else:
                    print(f"⚠️ Downloaded file is empty or doesn't exist")
                    return None
                    
        except aiohttp.ClientError as e:
            print(f"Network or client error occurred while downloading: {e}")
            return None
        except Exception as e:
            print(f"Error occurred while downloading song: {e}")
            return None
    return None

async def download_video(link: str):
    video_id = link.split('v=')[-1].split('&')[0]

    download_folder = "downloads"
    for ext in ["mp4", "webm", "mkv"]:
        file_path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(file_path):
            return file_path
        
    video_url = f"{VIDEO_API_URL}/video/{video_id}?api={API_KEY}"
    async with aiohttp.ClientSession() as session:
        for attempt in range(10):
            try:
                async with session.get(video_url) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status code {response.status}")
                
                    data = await response.json()
                    status = data.get("status", "").lower()

                    if status == "done":
                        download_url = data.get("link")
                        if not download_url:
                            raise Exception("API response did not provide a download URL.")
                        break
                    elif status == "downloading":
                        await asyncio.sleep(8)
                    else:
                        error_msg = data.get("error") or data.get("message") or f"Unexpected status '{status}'"
                        raise Exception(f"API error: {error_msg}")
            except Exception as e:
                print(f"[FAIL] {e}")
                return None
        else:
            print("⏱️ Max retries reached. Still downloading...")
            return None
    

        try:
            file_format = data.get("format", "mp4")
            file_extension = file_format.lower()
            file_name = f"{video_id}.{file_extension}"
            download_folder = "downloads"
            os.makedirs(download_folder, exist_ok=True)
            file_path = os.path.join(download_folder, file_name)

            async with session.get(download_url) as file_response:
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await file_response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                return file_path
        except aiohttp.ClientError as e:
            print(f"Network or client error occurred while downloading: {e}")
            return None
        except Exception as e:
            print(f"Error occurred while downloading video: {e}")
            return None
    return None

async def check_file_size(link):
    async def get_format_info(link):
        cookie_file = cookie_txt_file()
        if not cookie_file:
            print("No cookies found. Cannot check file size.")
            return None
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Try video API first
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
        except Exception as e:
            print(f"Video API failed: {e}")
        
        # Fallback to cookies
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return 0, "No cookies found. Cannot download video."
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return []
            
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_file} --user-agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return [], link
            
            ytdl_opts = {
                "quiet": True,
                "cookiefile": cookie_file,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                }
            }
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()
        
        def audio_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file:
                raise Exception("No cookies found. Cannot download audio.")
                
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_file,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file:
                raise Exception("No cookies found. Cannot download video.")
                
            ydl_optssx = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_file,
                "no_warnings": True,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-us,en;q=0.5",
                    "Sec-Fetch-Mode": "navigate",
                },
                "sleep_interval": 1,
                "max_sleep_interval": 5,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def song_video_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file:
                raise Exception("No cookies found. Cannot download song video.")
                
            formats = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_optssx = {
                "format": formats,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile" : cookie_file,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        def song_audio_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file:
                raise Exception("No cookies found. Cannot download song audio.")
                
            fpath = f"downloads/{title}.%(ext)s"
            ydl_optssx = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile" : cookie_file,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        # === MODIFIED DOWNLOAD LOGIC WITH CHANNEL CACHE PRIORITY ===
        if songvideo:
            query = title if title else link
            is_video = True
            
            # Extract video_id from link
            video_id = None
            try:
                if "youtube.com" in link or "youtu.be" in link:
                    if "v=" in link:
                        video_id = link.split('v=')[-1].split('&')[0]
                    elif "youtu.be/" in link:
                        video_id = link.split('youtu.be/')[-1].split('?')[0]
            except:
                pass
            
            # Step 1: Check channel cache first
            print(f"🔍 Checking channel cache for video: {query} (ID: {video_id})")
            cached_file_id = await check_channel_cache(query, video_id, is_video)
            if cached_file_id:
                print(f"✅ Found in channel cache: {query}")
                return cached_file_id, True
            
            # Step 2: Download from YouTube using yt-dlp with cookies
            if not video_id:
                print(f"⚠️ No video_id found in URL: {link}")
                return None, None
            
            cookie_file = cookie_txt_file()
            if not cookie_file:
                print("⚠️ No cookies available for download")
                return None, None
            
            try:
                print(f"🍪 Downloading with yt-dlp: {query} (ID: {video_id})")
                downloaded_file = await download_with_cookies(link, cookie_file)
                
                if downloaded_file and os.path.exists(downloaded_file):
                    print(f"✅ Downloaded successfully: {downloaded_file}")
                    
                    # Upload to channel and cache
                    cached_file_id = await save_to_channel_cache(query, downloaded_file, video_id, is_video)
                    
                    if cached_file_id:
                        # Clean up local file after successful upload (with safety check)
                        try:
                            if downloaded_file and os.path.exists(downloaded_file) and os.path.isfile(downloaded_file):
                                os.remove(downloaded_file)
                                print(f"🗑️ Cleaned up local file: {downloaded_file}")
                        except FileNotFoundError:
                            # File already removed, that's fine
                            pass
                        except Exception as e:
                            print(f"⚠️ Could not remove local file: {e}")
                        return cached_file_id, True
                    else:
                        # If upload failed, return local file path
                        print(f"⚠️ Upload failed, returning local file")
                        return downloaded_file, True
                else:
                    print(f"❌ Download failed: File not found")
                    return None, None
                    
            except Exception as e:
                print(f"❌ Download error: {e}")
                import traceback
                traceback.print_exc()
                return None, None
            
        elif songaudio:
            query = title if title else link
            is_video = False
            
            # Extract video_id/audio_id from link
            video_id = None
            try:
                if "youtube.com" in link or "youtu.be" in link:
                    if "v=" in link:
                        video_id = link.split('v=')[-1].split('&')[0]
                    elif "youtu.be/" in link:
                        video_id = link.split('youtu.be/')[-1].split('?')[0]
            except:
                pass
            
            # Step 1: Check channel cache first
            print(f"🔍 Checking channel cache for audio: {query} (ID: {video_id})")
            cached_file_id = await check_channel_cache(query, video_id, is_video)
            if cached_file_id:
                print(f"✅ Found in channel cache: {query}")
                return cached_file_id, True
            
            # Step 2: Download from YouTube using yt-dlp with cookies
            if not video_id:
                print(f"⚠️ No video_id found in URL: {link}")
                return None, None
            
            cookie_file = cookie_txt_file()
            if not cookie_file:
                print("⚠️ No cookies available for download")
                return None, None
            
            try:
                print(f"🍪 Downloading with yt-dlp: {query} (ID: {video_id})")
                downloaded_file = await download_with_cookies(link, cookie_file)
                
                if downloaded_file and os.path.exists(downloaded_file):
                    print(f"✅ Downloaded successfully: {downloaded_file}")
                    
                    # Upload to channel and cache
                    cached_file_id = await save_to_channel_cache(query, downloaded_file, video_id, is_video)
                    
                    if cached_file_id:
                        # Clean up local file after successful upload (with safety check)
                        try:
                            if downloaded_file and os.path.exists(downloaded_file) and os.path.isfile(downloaded_file):
                                os.remove(downloaded_file)
                                print(f"🗑️ Cleaned up local file: {downloaded_file}")
                        except FileNotFoundError:
                            # File already removed, that's fine
                            pass
                        except Exception as e:
                            print(f"⚠️ Could not remove local file: {e}")
                        return cached_file_id, True
                    else:
                        # If upload failed, return local file path
                        print(f"⚠️ Upload failed, returning local file")
                        return downloaded_file, True
                else:
                    print(f"❌ Download failed: File not found")
                    return None, None
                    
            except Exception as e:
                print(f"❌ Download error: {e}")
                import traceback
                traceback.print_exc()
                return None, None
            
        elif video:
            # Try video API first
            try:
                downloaded_file = await download_video(link)
                if downloaded_file:
                    direct = True
                    return downloaded_file, direct
            except Exception as e:
                print(f"Video API failed: {e}")
            
            # Fallback to cookies
            cookie_file = cookie_txt_file()
            if not cookie_file:
                print("No cookies found. Cannot download video.")
                return None, None
                
            if await is_on_off(1):
                direct = True
                downloaded_file = await download_song(link)
            else:
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp",
                    "--cookies", cookie_file,
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]",
                    f"{link}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = False
                else:
                   file_size = await check_file_size(link)
                   if not file_size:
                     print("None file Size")
                     return None, None
                   total_size_mb = file_size / (1024 * 1024)
                   if total_size_mb > 250:
                     print(f"File size {total_size_mb:.2f} MB exceeds the 100MB limit.")
                     return None, None
                   direct = True
                   downloaded_file = await loop.run_in_executor(None, video_dl)
        else:
            # === MAIN LOGIC: CHANNEL CACHE FIRST, THEN YOUTUBE SEARCH + SAAVN PLAY ===
            # Extract query from link or use as-is
            query = link
            is_video = False  # Default to audio
            
            # If it's a YouTube URL, try to get title first
            if "youtube.com" in link or "youtu.be" in link:
                try:
                    print(f"🎬 Extracting title from YouTube URL: {link}")
                    title_result = await self.title(link)
                    query = title_result
                    print(f"📝 Extracted title: {title_result}")
                except Exception as e:
                    print(f"⚠️ Could not extract YouTube title: {e}")
                    query = link
            elif "watch?v=" in link:
                try:
                    video_id = link.split('v=')[-1].split('&')[0]
                    query = f"youtube video {video_id}"
                except:
                    query = link
            
            # Extract video_id from link
            video_id = None
            try:
                if "youtube.com" in link or "youtu.be" in link:
                    if "v=" in link:
                        video_id = link.split('v=')[-1].split('&')[0]
                    elif "youtu.be/" in link:
                        video_id = link.split('youtu.be/')[-1].split('?')[0]
            except:
                pass
            
            # Step 1: Check channel cache first
            print(f"🔍 Checking channel cache for: {query} (ID: {video_id})")
            cached_file_id = await check_channel_cache(query, video_id, is_video)
            
            if cached_file_id:
                print(f"✅ Found in channel cache: {query}")
                # Return file_id which can be used directly
                return cached_file_id, True
            
            # Step 2: If not in cache, download from YouTube and upload to channel
            if not video_id:
                print(f"⚠️ No video_id found in URL: {link}")
                return None, None
            
            print(f"📥 Not in cache, downloading from YouTube: {query} (ID: {video_id})")
            
            # Download directly from YouTube using yt-dlp with cookies
            cookie_file = cookie_txt_file()
            if not cookie_file:
                print("⚠️ No cookies available for download")
                return None, None
            
            try:
                # Download using yt-dlp with cookies
                print(f"🍪 Downloading with yt-dlp: {link}")
                downloaded_file = await download_with_cookies(link, cookie_file)
                
                if downloaded_file and os.path.exists(downloaded_file):
                    print(f"✅ Downloaded successfully: {downloaded_file}")
                    
                    # Upload to channel and cache
                    print(f"📤 Uploading to channel cache: {query} (Video ID: {video_id})")
                    cached_file_id = await save_to_channel_cache(query, downloaded_file, video_id, is_video)
                    
                    if cached_file_id:
                        print(f"✅ Uploaded and cached successfully: {query}")
                        # Clean up local file after successful upload (with safety check)
                        try:
                            if downloaded_file and os.path.exists(downloaded_file) and os.path.isfile(downloaded_file):
                                os.remove(downloaded_file)
                                print(f"🗑️ Cleaned up local file: {downloaded_file}")
                        except FileNotFoundError:
                            # File already removed, that's fine
                            pass
                        except Exception as e:
                            print(f"⚠️ Could not remove local file: {e}")
                        return cached_file_id, True
                    else:
                        # If upload failed, return local file path
                        print(f"⚠️ Upload failed, returning local file: {downloaded_file}")
                        return downloaded_file, True
                else:
                    print(f"❌ Download failed: File not found")
                    return None, None
                    
            except Exception as e:
                print(f"❌ Download error: {e}")
                import traceback
                traceback.print_exc()
                return None, None
            
        return None, None

# === OPTIMIZED TOP 1 SEARCH: YOUTUBE + JIO SAAVN ===
async def optimized_top1_youtube_saavn_play(query: str):
    """
    Optimized search that gets ONLY the top 1 YouTube result and plays it with Jio Saavn API
    No multiple searches, no complex matching - just top result + Saavn
    """
    print(f"🎵 Starting optimized top 1 search for: {query}")
    
    try:
        # Step 1: Get ONLY the top 1 YouTube result
        print(f"🔍 Getting top 1 YouTube result for: {query}")
        results = VideosSearch(query, limit=1)
        search_results = await results.next()
        
        if not search_results.get("result"):
            print("❌ No YouTube results found")
            return None, None, False
        
        # Step 2: Get the single top result
        top_result = search_results["result"][0]
        youtube_title = top_result["title"]
        youtube_artist = top_result.get("channel", {}).get("name", "Unknown")
        youtube_duration = top_result.get("duration", "Unknown")
        youtube_url = top_result["link"]
        youtube_video_id = top_result.get("id", "")
        
        # Extract video_id from URL if not in result
        if not youtube_video_id and "youtube.com" in youtube_url:
            try:
                if "v=" in youtube_url:
                    youtube_video_id = youtube_url.split('v=')[-1].split('&')[0]
                elif "youtu.be/" in youtube_url:
                    youtube_video_id = youtube_url.split('youtu.be/')[-1].split('?')[0]
            except:
                pass
        
        print(f"📺 Top 1 YouTube result: {youtube_title} (ID: {youtube_video_id})")
        
        # Step 3: Try yt-dlp with cookies FIRST (priority)
        print(f"🍪 Trying yt-dlp with cookies (FIRST PRIORITY) for: {youtube_title}")
        print(f"📺 YouTube URL: {youtube_url}")
        
        try:
            cookie_file = cookie_txt_file()
            
            if cookie_file:
                print(f"🍪 Using cookies file: {cookie_file}")
                try:
                    # Try to download using yt-dlp with cookies
                    downloaded_file = await download_with_cookies(youtube_url, cookie_file)
                    if downloaded_file and os.path.exists(downloaded_file):
                        youtube_info = {
                            "title": youtube_title,
                            "artist": youtube_artist,
                            "source": "YouTube (yt-dlp)",
                            "quality": "High",
                            "duration": youtube_duration,
                            "video_id": youtube_video_id
                        }
                        print(f"✅ Downloaded with yt-dlp: {youtube_title} (ID: {youtube_video_id})")
                        return downloaded_file, youtube_info, False
                    else:
                        print("⚠️ yt-dlp download returned no file")
                except Exception as e:
                    print(f"⚠️ yt-dlp cookies download failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("⚠️ No cookies found, trying Saavn")
        except Exception as e:
            print(f"⚠️ Error getting cookie file: {e}")
        
        # Step 4: Fallback to Jio Saavn API with the exact title
        print(f"🔍 yt-dlp failed, trying Jio Saavn API with: {youtube_title}")
        saavn_url, saavn_info = await download_saavn_song(youtube_title)
        
        if saavn_url:
            print(f"✅ SUCCESS! Playing from Jio Saavn: {saavn_info['title']} by {saavn_info['artist']}")
            return saavn_url, saavn_info, True
        
        # Step 5: If Saavn fails, try with cleaned title
        print(f"🔍 Trying Jio Saavn with cleaned title...")
        cleaned_title = clean_youtube_title_for_saavn(youtube_title)
        saavn_url, saavn_info = await download_saavn_song(cleaned_title)
        
        if saavn_url:
            print(f"✅ SUCCESS! Playing from Jio Saavn: {saavn_info['title']} by {saavn_info['artist']}")
            return saavn_url, saavn_info, True
        
        # Step 6: Final fallback to regular YouTube download
        print(f"🔄 Final fallback to regular YouTube download: {youtube_title}")
        try:
            downloaded_file = await download_song(youtube_url)
            
            if downloaded_file and os.path.exists(downloaded_file):
                youtube_info = {
                    "title": youtube_title,
                    "artist": youtube_artist,
                    "source": "YouTube",
                    "quality": "Variable",
                    "duration": youtube_duration,
                    "video_id": youtube_video_id
                }
                print(f"✅ Downloaded from YouTube: {youtube_title} (ID: {youtube_video_id})")
                return downloaded_file, youtube_info, False
            else:
                print("❌ Failed to download from YouTube")
        except Exception as e:
            print(f"❌ Regular YouTube download failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Optimized search error: {e}")
    
    print(f"❌ All methods failed for: {query}")
    return None, None, False

# === ORIGINAL HYBRID SEARCH: YOUTUBE SEARCH + SAAVN PLAY ===
async def youtube_search_saavn_play(query: str):
    """
    Use YouTube search to find songs, then play from Saavn API for better quality
    """
    print(f"🎵 Starting hybrid search: YouTube → Saavn for: {query}")
    
    try:
        # Step 1: Search YouTube to find the song
        print(f"🔍 Searching YouTube for: {query}")
        results = VideosSearch(query, limit=5)  # Get multiple results for better matching
        search_results = await results.next()
        
        if not search_results.get("result"):
            print("❌ No YouTube results found")
            return None, None, False
        
        # Step 2: Extract song titles from YouTube results
        youtube_results = search_results["result"]
        print(f"📺 Found {len(youtube_results)} YouTube results")
        
        # Step 3: Try each YouTube result with Saavn using multiple search variations
        for i, result in enumerate(youtube_results, 1):
            youtube_title = result["title"]
            youtube_artist = result.get("channel", {}).get("name", "Unknown")
            youtube_duration = result.get("duration", "Unknown")
            
            print(f"\n🎯 Trying result {i}: {youtube_title}")
            
            # Clean the YouTube title for Saavn search
            saavn_query = clean_youtube_title_for_saavn(youtube_title)
            print(f"🧹 Cleaned title for Saavn: {saavn_query}")
            
            # Generate multiple search variations
            search_variations = generate_search_variations(saavn_query)
            print(f"🔍 Trying {len(search_variations)} search variations")
            
            # Try each variation
            for j, variation in enumerate(search_variations, 1):
                print(f"   Variation {j}: '{variation}'")
                saavn_url, saavn_info = await download_saavn_song(variation)
                
                if saavn_url:
                    # Check if this is a good match (not from a different movie/album)
                    found_title = saavn_info['title'].lower()
                    original_query = query.lower()
                    
                    # Check if the found song title contains the original query words
                    query_words = original_query.split()
                    title_words = found_title.split()
                    
                    # Count matching words
                    matching_words = sum(1 for word in query_words if word in title_words)
                    match_percentage = (matching_words / len(query_words)) * 100 if query_words else 0
                    
                    print(f"   ✅ Found: {saavn_info['title']} (Match: {match_percentage:.0f}%)")
                    
                    # Only accept if it's a good match (at least 60% word match)
                    if match_percentage >= 60:
                        print(f"✅ SUCCESS! Found on Saavn: {saavn_info['title']} by {saavn_info['artist']}")
                        return saavn_url, saavn_info, True
                    else:
                        print(f"   ⚠️  Poor match, trying next variation...")
                        continue
                else:
                    print(f"   ❌ Not found with variation: '{variation}'")
            
            print(f"❌ No good matches found for: {youtube_title}")
        
        # Step 4: If no Saavn match found, fallback to YouTube download
        print(f"🔄 No Saavn matches found, falling back to YouTube")
        best_result = youtube_results[0]  # Use first result
        video_url = best_result["link"]
        
        print(f"⬇️ Downloading from YouTube: {best_result['title']}")
        downloaded_file = await download_song(video_url)
        
        if downloaded_file:
            youtube_info = {
                "title": best_result["title"],
                "artist": best_result.get("channel", {}).get("name", "YouTube"),
                "source": "YouTube",
                "quality": "Variable",
                "duration": best_result.get("duration", "Unknown")
            }
            print(f"✅ Downloaded from YouTube: {best_result['title']}")
            return downloaded_file, youtube_info, False
        else:
            print("❌ Failed to download from YouTube")
            
    except Exception as e:
        print(f"❌ Hybrid search error: {e}")
    
    print(f"❌ All methods failed for: {query}")
    return None, None, False

def clean_youtube_title_for_saavn(youtube_title: str):
    """Clean YouTube title to make it suitable for Saavn search"""
    # Remove common YouTube suffixes and extra words
    suffixes_to_remove = [
        "official video", "official music video", "official", "music video", 
        "lyrics", "lyric video", "lyrics video", "hd", "4k", "full song",
        "song", "video", "audio", "cover", "remix", "version", "mix",
        "official audio", "official lyric video", "official hd", "official 4k",
        "full 4k video", "full hd", "full song hd", "full song 4k"
    ]
    
    # Remove common actor/artist names that might interfere
    actor_names = [
        "amitabh bachchan", "jaya prada", "kishore kumar", "lata mangeshkar",
        "mohammed rafi", "asha bhosle", "kumar sanu", "udit narayan",
        "alisha chinai", "anuradha paudwal", "sonu nigam", "shreya ghoshal"
    ]
    
    title = youtube_title.lower().strip()
    
    # Remove suffixes
    for suffix in suffixes_to_remove:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
    
    # Remove extra words in parentheses or brackets
    title = re.sub(r'\([^)]*\)', '', title)  # Remove (Official Video)
    title = re.sub(r'\[[^\]]*\]', '', title)  # Remove [HD]
    
    # Remove pipe separators and everything after them
    if '|' in title:
        title = title.split('|')[0].strip()
    
    # Remove common prefixes
    prefixes_to_remove = ["watch:", "listen:", "play:", "song:"]
    for prefix in prefixes_to_remove:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
    
    # Remove actor names that might interfere with search
    for actor in actor_names:
        title = title.replace(actor, '').strip()
    
    # Remove special characters and extra spaces
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    
    # For movie songs, try to keep the complete song title
    # Don't truncate too aggressively for movie songs
    words = title.split()
    if len(words) > 4:  # Allow more words for movie songs
        # Try to keep the most important words (usually the first 4)
        title = ' '.join(words[:4])
    
    return title

def generate_search_variations(query: str):
    """Generate multiple search variations for better matching"""
    variations = []
    
    # Original query
    variations.append(query)
    
    # Remove common words that might interfere
    words = query.split()
    if len(words) > 2:
        # Try without last word
        variations.append(' '.join(words[:-1]))
        
        # Try with just first two words
        if len(words) >= 2:
            variations.append(' '.join(words[:2]))
    
    # Add quotes for exact phrase search
    variations.append(f'"{query}"')
    
    # Add common Hindi song suffixes
    hindi_suffixes = ['song', 'geet', 'gaan']
    for suffix in hindi_suffixes:
        variations.append(f"{query} {suffix}")
    
    return variations

# === NEW FUNCTION FOR HYBRID DOWNLOAD ===
async def download_with_saavn_priority(query: str):
    """
    Download function using hybrid approach: YouTube search + Saavn play
    """
    print(f"🎵 Starting hybrid download process for: {query}")
    
    # Use the new hybrid search function
    return await youtube_search_saavn_play(query)

# === TEST FUNCTION FOR OPTIMIZED TOP 1 SEARCH ===
async def test_optimized_search(query: str):
    """
    Test function to demonstrate the optimized top 1 search functionality
    """
    print(f"🧪 Testing optimized top 1 search for: {query}")
    
    try:
        # Test the optimized top 1 search
        download_url, song_info, is_saavn = await optimized_top1_youtube_saavn_play(query)
        
        if download_url:
            if is_saavn:
                print(f"✅ SUCCESS! Found on Jio Saavn: {song_info['title']} by {song_info['artist']}")
                print(f"🔗 Download URL: {download_url[:50]}...")
                print(f"📊 Quality: {song_info['quality']}")
            else:
                print(f"✅ SUCCESS! Downloaded from YouTube: {song_info['title']}")
                print(f"📁 File path: {download_url}")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

# === LEGACY TEST FUNCTION ===
async def test_improved_search(query: str):
    """
    Legacy test function - now redirects to optimized search
    """
    return await test_optimized_search(query)

 # ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎

# 🧑‍💻 Developer : t.me/brahix
# 🔗 Source link : GitHub.com/suraj08832/Sonali-MusicV2
# 📢 Telegram channel : t.me/about_brahix
# =======================================================
>>>>>>> Incoming (Background Agent changes)
