from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram import Client, filters, enums 

import config
from SONALI_MUSIC import app

class BUTTONS(object):
    BBUTTON = [
        [
            InlineKeyboardButton("ᴄʜᴧᴛ-ɢᴘᴛ", callback_data="TOOL_BACK HELP_01"),
            InlineKeyboardButton("ғυη", callback_data="TOOL_BACK HELP_11"),
            InlineKeyboardButton("ᴄσᴜᴘʟєs", callback_data="TOOL_BACK HELP_08"),
        ],
        [
            InlineKeyboardButton("sєᴧʀᴄʜ", callback_data="TOOL_BACK HELP_02"),
            InlineKeyboardButton("ᴛʀᴧηsʟᴧᴛє", callback_data="TOOL_BACK HELP_24"),
            InlineKeyboardButton("ɪηғσ", callback_data="TOOL_BACK HELP_04"),
        ],
        [
            InlineKeyboardButton("ғσηᴛ", callback_data="TOOL_BACK HELP_05"),
            InlineKeyboardButton("ᴡʜɪsᴘєʀ", callback_data="TOOL_BACK HELP_03"),
            InlineKeyboardButton("ᴛᴧɢᴧʟʟ", callback_data="TOOL_BACK HELP_07"),
        ],
        [
            InlineKeyboardButton("ɢᴧϻє", callback_data="TOOL_BACK HELP_21"),
            InlineKeyboardButton("sєᴛᴜᴘ", callback_data="TOOL_BACK HELP_17"),
            InlineKeyboardButton("ǫυσᴛʟʏ", callback_data="TOOL_BACK HELP_12"),
        ],
        [
            InlineKeyboardButton("ɢɪᴛʜᴜʙ", callback_data="TOOL_BACK HELP_25"),
            InlineKeyboardButton("Ⓣ-ɢʀᴧᴘʜ", callback_data=f"TOOL_BACK HELP_26"),
            InlineKeyboardButton("sᴛɪᴄᴋєʀs", callback_data="TOOL_BACK HELP_10"),
        ],
        [InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data=f"MAIN_CP")]
    ]
    
    
    MBUTTON = [

        [
            InlineKeyboardButton("ᴀɴᴛɪ ғʟᴏᴏᴅ", callback_data="MANAGEMENT_BACK HELP_28"),
            InlineKeyboardButton("ᴀᴘᴘʀᴏᴠᴀʟ", callback_data="MANAGEMENT_BACK HELP_29"),
            InlineKeyboardButton("ʙᴜɢs", callback_data="MANAGEMENT_BACK HELP_30"),
        ],
        [
            InlineKeyboardButton("ᴄᴏᴜɴᴛʀʏ", callback_data="MANAGEMENT_BACK HELP_31"),
            InlineKeyboardButton("ᴘᴜʀɢᴇ", callback_data="MANAGEMENT_BACK HELP_32"),
            InlineKeyboardButton("ᴘʏᴛʜᴏɴ", callback_data="MANAGEMENT_BACK HELP_33"),
        ],
        [
            InlineKeyboardButton("ʀᴀɴᴋɪɴɢ", callback_data="MANAGEMENT_BACK HELP_34"),
            InlineKeyboardButton("ʀᴛᴍᴘ ʟɪᴠᴇ", callback_data="MANAGEMENT_BACK HELP_35"),
            InlineKeyboardButton("ᴠᴄ ᴛᴏᴏʟs", callback_data="MANAGEMENT_BACK HELP_36"),
        ],
        [
            InlineKeyboardButton("ᴧᴄᴛɪση", callback_data="MANAGEMENT_BACK HELP_14"),
            InlineKeyboardButton("ʜɪsᴛᴏʀʏ", callback_data="MANAGEMENT_BACK HELP_23"),
            InlineKeyboardButton("ᴛᴛs", callback_data="MANAGEMENT_BACK HELP_27"),
        ],
        [
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data=f"MAIN_CP"), 
        ]
        ]
    PBUTTON = [
        [
            InlineKeyboardButton("˹ ᴄσηᴛᴧᴄᴛ ˼", url="https://t.me/TheSigmaCoder"),
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="MAIN_CP"),
        ]
        ]
    
    ABUTTON = [
        [
            InlineKeyboardButton("˹ sυᴘᴘσʀᴛ ˼", url="https://t.me/PURVI_BOTS"),
            InlineKeyboardButton("˹ υᴘᴅᴧᴛєs ˼", url="https://t.me/+gMy8Cp190ediNzZl"),
        ],
        [  
            InlineKeyboardButton("˹ ᴘʀɪᴠᴧᴄʏ ˼", url="https://telegra.ph/Privacy-Policy--Purvi-Bots-by-ALPHA-BABY-08-06"),
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="settingsback_helper"),
        ]
        ]
    
    SBUTTON = [
        [
            InlineKeyboardButton("ϻᴜѕɪᴄ", callback_data="settings_back_helper"),
            InlineKeyboardButton("ϻᴧηᴧɢєϻєηᴛ", callback_data="TOOL_CP"),
        ],
        [
            InlineKeyboardButton("ɴᴇᴡ ᴍᴏᴅᴜʟᴇs", callback_data="MANAGEMENT_CP"),
            
        ],
        [
            InlineKeyboardButton("ᴧʟʟ ʙσᴛ's", callback_data="MAIN_BACK HELP_ABOUT"),
            InlineKeyboardButton("ᴘʀσϻσᴛɪση", callback_data="PROMOTION_CP"),
        ],
        [
            InlineKeyboardButton("⌯ ʙᴧᴄᴋ ᴛσ ʜσϻє ⌯", callback_data="settingsback_helper"),
            
        ]
        ]



