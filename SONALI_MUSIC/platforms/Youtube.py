# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀

# This source code is under MIT License 📜 Unauthorized forking, importing, or using this code without giving proper credit will result in legal action ⚠️
 
# 📩 DM for permission : @brahix
# =======================================================


import asyncio
import os
import re
import json
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
import config
#from config import API_URL, VIDEO_API_URL, API_KEY
from os import getenv

API_URL = getenv("API_URL", 'https://api.thequickearn.xyz')
API_KEY = getenv("API_KEY", 'NxGBNexGenBotsa02f5a')
VIDEO_API_URL = getenv("VIDEO_API_URL", 'https://api.video.thequickearn.xyz')

# === SAAVN API CONFIGURATION ===
SAVN_API_BASE = "https://apikeyy-zeta.vercel.app/api/search"
SAVN_SONGS_API = "https://apikeyy-zeta.vercel.app/api/songs"

def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"
    if not os.path.exists(cookie_dir):
        return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file

# === SAAVN API FUNCTIONS ===
def clean_query(query: str):
    """Clean and optimize search query"""
    # Remove common words that might interfere with search
    stop_words = ['song', 'music', 'video', 'official', 'lyrics', 'hd', '4k', 'full']
    query = query.lower().strip()
    
    # Remove stop words
    words = query.split()
    cleaned_words = [word for word in words if word not in stop_words]
    
    # Join back and clean
    cleaned_query = ' '.join(cleaned_words)
    
    # Remove extra spaces and special characters
    cleaned_query = re.sub(r'[^\w\s]', '', cleaned_query)
    cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
    
    return cleaned_query

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
        
        # Strategy 3: Try with different variations
        query_variations = [
            query.replace(" ", ""),  # Remove spaces
            query.split()[0] if len(query.split()) > 1 else query,  # First word only
            query.split()[-1] if len(query.split()) > 1 else query,  # Last word only
        ]
        
        for variation in query_variations:
            if variation != query and variation != cleaned_query:
                print(f"🔍 Trying variation: {variation}")
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
    video_id = link.split('v=')[-1].split('&')[0]

    download_folder = "downloads"
    for ext in ["mp3", "m4a", "webm"]:
        file_path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(file_path):
            #print(f"File already exists: {file_path}")
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
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_file} --playlist-end {limit} --skip-download {link}"
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
            
        ytdl_opts = {"quiet": True, "cookiefile" : cookie_file}
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

        # === MODIFIED DOWNLOAD LOGIC WITH SAAVN PRIORITY ===
        if songvideo:
            # Try Saavn first for song video
            saavn_url, saavn_info = await download_saavn_song(title if title else link)
            if saavn_url:
                print(f"✅ Downloaded from Saavn: {saavn_info['title']}")
                return saavn_url, True
            
            # Fallback to YouTube
            await download_song(link)
            fpath = f"downloads/{link}.mp3"
            return fpath, False
            
        elif songaudio:
            # Try Saavn first for song audio
            saavn_url, saavn_info = await download_saavn_song(title if title else link)
            if saavn_url:
                print(f"✅ Downloaded from Saavn: {saavn_info['title']}")
                return saavn_url, True
            
            # Fallback to YouTube
            await download_song(link)
            fpath = f"downloads/{link}.mp3"
            return fpath, False
            
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
            # === MAIN LOGIC: YOUTUBE SEARCH + SAAVN PLAY ===
            # Extract query from link or use as-is
            query = link
            
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
            
            # Use hybrid search: YouTube search + Saavn play
            print(f"🔍 Using hybrid search for: {query}")
            download_url, song_info, is_saavn = await youtube_search_saavn_play(query)
            
            if download_url:
                if is_saavn:
                    print(f"✅ Downloaded from Saavn: {song_info['title']} by {song_info['artist']}")
                    return download_url, True
                else:
                    print(f"✅ Downloaded from YouTube: {song_info['title']}")
                    return download_url, True
            else:
                print(f"❌ All methods failed for: {query}")
                return None, None
            
        return None, None

# === HYBRID SEARCH: YOUTUBE SEARCH + SAAVN PLAY ===
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

 # ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎

# 🧑‍💻 Developer : t.me/brahix
# 🔗 Source link : GitHub.com/suraj08832/Sonali-MusicV2
# 📢 Telegram channel : t.me/about_brahix
# =======================================================
