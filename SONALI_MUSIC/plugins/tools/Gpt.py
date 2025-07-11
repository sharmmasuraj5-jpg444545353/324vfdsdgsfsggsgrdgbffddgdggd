import time
import requests
from SONALI_MUSIC import app
from config import BOT_USERNAME
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_URL = "https://chatgpt.apinepdev.workers.dev/?question="

@app.on_message(filters.command(["chatgpt", "ai", "ask", "gpt", "solve"], prefixes=["+", ".", "/", "-", "", "$", "#", "&"]))
async def chat_gpt(bot, message):
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        if len(message.command) < 2:
            return await message.reply_text(
                "Example:\n\n`/chatgpt Where is the Taj Mahal?`",
                parse_mode=ParseMode.MARKDOWN
            )

        question = message.text.split(' ', 1)[1]
        response = requests.get(f"{API_URL}{question}")

        if response.status_code == 200:
            json_data = response.json()

            if "answer" in json_data:
                answer = json_data["answer"]

                # Unwanted phrases remove
                unwanted_phrases = [
                    "Join our community",
                    "t.me/",
                    "Answered by",
                    "Join our Telegram"
                ]
                for phrase in unwanted_phrases:
                    if phrase.lower() in answer.lower():
                        answer = answer.split(phrase)[0].strip()

                # Inline Add Me Button
                buttons = InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{app.username}?startgroup=true")
                    ]]
                )

                return await message.reply_text(
                    f"**🤖 ChatGPT Response:**\n\n{answer}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=buttons
                )
            else:
                return await message.reply_text("⚠️ No valid answer found in the response.")
        else:
            return await message.reply_text(f"⚠️ API Error: Received status code {response.status_code}")

    except Exception as e:
        return await message.reply_text(f"⚠️ **Error:** `{str(e)}`", parse_mode=ParseMode.MARKDOWN)
