import asyncio
import os
import re
import json
from typing import Union
import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from SONALI_MUSIC.utils.database import is_on_off
from SONALI_MUSIC.utils.formatters import time_to_seconds
import random
import logging

# Old API you had
NEW_API_URL = "https://apikeyy-zeta.vercel.app/api"
# The new API you want to add
EYAPI_URL = "https://eyapi001-c4f7b52ccfc4.herokuapp.com/query"

def cookie_txt_file():
    cookie_dir = os.path.join(os.getcwd(), "cookies")
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        raise FileNotFoundError("No cookie .txt files found in cookies directory")
    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file

async def download_song(link: str, query: str = None, video: bool = False):
    """Try EYAPI first (when query provided), then NEW_API_URL, else fallback to cookies + yt-dlp."""
    # 1. Prefer EYAPI when we have a query (your domain first)
    if query:
        async with aiohttp.ClientSession() as session:
            params = {"query": query, "video": "true" if video else "false"}
            try:
                async with session.get(EYAPI_URL, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        download_url = data.get("link") or data.get("url")
                        if download_url:
                            # Use a stable name based on query
                            return await download_file(session, download_url, "eyapi_" + str(hash((query, video))), data)
                    else:
                        logging.warning(f"EYAPI responded {resp.status} for query {query}")
            except Exception:
                logging.exception("Error calling EYAPI")

    # 2. Try NEW_API_URL when we have a direct YouTube link
    video_id = link.split('v=')[-1].split('&')[0] if link else None
    if video_id:
        # Check if already downloaded
        download_folder = "downloads"
        for ext in ["mp3", "m4a", "webm", "mp4", "mkv"]:
            file_path = os.path.join(download_folder, f"{video_id}.{ext}")
            if os.path.exists(file_path):
                return file_path

        async with aiohttp.ClientSession() as session:
            try:
                new_song_url = f"{NEW_API_URL}/song/{video_id}"
                async with session.get(new_song_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        download_url = data.get("link") or data.get("url")
                        if download_url:
                            file_path = await download_file(session, download_url, video_id, data)
                            if file_path:
                                return file_path
                    else:
                        logging.warning(f"NEW_API_URL failed with status {resp.status}")
            except Exception:
                logging.exception("Error in NEW_API_URL download attempt")

    # 3. Fallback: use yt-dlp + cookies
    logging.info("Falling back to yt‑dlp + cookies method")
    if video:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: yt_video_download_with_audio(link))
    return await asyncio.get_event_loop().run_in_executor(None, lambda: yt_audio_download(link))


async def download_file(session, download_url, video_id, data):
    """Helper to download file from URL"""
    try:
        file_format = data.get("format", "mp3")
        ext = file_format.lower()
        file_name = f"{video_id}.{ext}"
        download_folder = "downloads"
        os.makedirs(download_folder, exist_ok=True)
        file_path = os.path.join(download_folder, file_name)

        async with session.get(download_url) as file_resp:
            if file_resp.status != 200:
                logging.warning(f"Download URL responded with status {file_resp.status}")
                return None
            with open(file_path, "wb") as f:
                while True:
                    chunk = await file_resp.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        return file_path
    except Exception as e:
        logging.exception("Error in download_file")
        return None

async def check_file_size(link):
    """Get total filesize of all formats for a YouTube link via yt‑dlp + cookies."""
    async def get_format_info(link):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logging.error(f"yt-dlp failed: {stderr.decode().strip()}")
            return None
        return json.loads(stdout.decode())

    info = await get_format_info(link)
    if not info or "formats" not in info:
        return None
    total = 0
    for fmt in info["formats"]:
        # Some formats might not have filesize
        fs = fmt.get("filesize")
        if fs:
            total += fs
    return total

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if err:
        errstr = err.decode("utf-8", errors="ignore")
        if "unavailable videos are hidden" in errstr.lower():
            return out.decode("utf-8", errors="ignore")
        else:
            logging.error(f"Shell cmd error: {errstr}")
    return out.decode("utf-8", errors="ignore")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.reg_ansi = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            text = message.text or message.caption or ""
            if message.entities:
                for ent in message.entities:
                    if ent.type == MessageEntityType.URL:
                        return text[ent.offset : ent.offset + ent.length]
            if message.caption_entities:
                for ent in message.caption_entities:
                    if ent.type == MessageEntityType.TEXT_LINK:
                        return ent.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        vsearch = VideosSearch(link, limit=1)
        res = await vsearch.next()
        r = res["result"][0]
        title = r["title"]
        duration_min = r["duration"]
        thumbnail = r["thumbnails"][0]["url"].split("?")[0]
        vidid = r["id"]
        duration_sec = 0
        if duration_min != "None":
            duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    # ... other methods like title(), duration(), thumbnail() unchanged ...

    async def download(
        self,
        link: str = None,
        query: str = None,
        video: bool = False,
        songaudio: bool = False,
        songvideo: bool = False,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> Union[str, None]:
        """
        Download logic:
        - If query given, try EYAPI first.
        - Else if you have a YouTube link, use your existing flows.
        """

        # If the user provided a query instead of link, try EYAPI
        if query:
            async with aiohttp.ClientSession() as session:
                params = {
                    "query": query,
                    "video": "true" if video else "false"
                }
                try:
                    async with session.get(EYAPI_URL, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            # Expect data to contain link/url to download
                            download_url = data.get("link") or data.get("url")
                            if download_url:
                                # choose an extension or format if given
                                return await download_file(session, download_url, "eyapi_"+str(hash(query)), data)
                        else:
                            logging.warning(f"EYAPI responded {resp.status} for query {query}")
                except Exception as e:
                    logging.exception("Error calling EYAPI")

            # If EYAPI fails, fallthrough to using link or search + yt-dlp

        # If no link given but we got query, do a YT search to get link
        if not link and query:
            # get top result from VideosSearch
            vs = VideosSearch(query, limit=1)
            res = await vs.next()
            link = res["result"][0]["link"]
            if "&" in link:
                link = link.split("&")[0]

        if not link:
            logging.error("No link or query provided to download()")
            return None

        # Now link-based download paths (existing logic)
        # Cases: video, songaudio, songvideo, etc.

        # If video path
        if video:
            # Depending on your config flag is_on_off(1)
            if await is_on_off(1):
                # Try your custom APIs first
                file_from_custom = await download_song(link, query=query, video=True)
                if file_from_custom:
                    return file_from_custom
                # Fallback to checking file size / streaming link etc
                file_size = await check_file_size(link)
                if file_size:
                    total_mb = file_size / (1024 * 1024)
                    if total_mb > 250:
                        logging.warning(f"Video too large: {total_mb:.2f} MB")
                        return None
                # Download video via yt‑dlp
                video_path = await asyncio.get_event_loop().run_in_executor(None, lambda: yt_video_download(link))
                return video_path

            else:
                # If direct streaming allowed
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp",
                    "--cookies", cookie_txt_file(),
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]",
                    link,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    stream_url = stdout.decode().split("\n")[0]
                    return stream_url
                # fallback to file download if needed
                file_size = await check_file_size(link)
                if file_size:
                    total_mb = file_size / (1024 * 1024)
                    if total_mb > 250:
                        logging.warning(f"Video too large: {total_mb:.2f} MB")
                        return None
                video_path = await asyncio.get_event_loop().run_in_executor(None, lambda: yt_video_download(link))
                return video_path

        elif songaudio or songvideo:
            # First attempt custom API download
            file_from_custom = await download_song(link, query=query, video=songvideo)
            if file_from_custom:
                return file_from_custom
            # Fallback: download via yt‑dlp with appropriate options
            # For audio:
            if songaudio:
                return await asyncio.get_event_loop().run_in_executor(None, lambda: yt_audio_download(link))
            # For video with audio:
            if songvideo:
                return await asyncio.get_event_loop().run_in_executor(None, lambda: yt_video_download_with_audio(link))

        else:
            # Default fallback: audio download
            return await asyncio.get_event_loop().run_in_executor(None, lambda: yt_audio_download(link))


# You need to define these helpers, for example:

def yt_audio_download(link: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "cookiefile": cookie_txt_file(),
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        outfile = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if os.path.exists(outfile):
            return outfile
        ydl.download([link])
        return outfile

def yt_video_download(link: str) -> str:
    opts = {
        "format": "best[height<=?720][width<=?1280]",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "cookiefile": cookie_txt_file(),
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(link, download=False)
        outfile = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if os.path.exists(outfile):
            return outfile
        ydl.download([link])
        return outfile

def yt_video_download_with_audio(link: str) -> str:
    # Combining best video + audio
    opts = {
        "format": "(bestvideo[height<=?720][width<=?1280])+(bestaudio[ext=m4a])",
        "merge_output_format": "mp4",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "cookiefile": cookie_txt_file(),
        "no_warnings": True,
        "prefer_ffmpeg": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(link, download=False)
        outfile = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if os.path.exists(outfile):
            return outfile
        ydl.download([link])
        return outfile
