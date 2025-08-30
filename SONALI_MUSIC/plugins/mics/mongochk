from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import re, json, io, os
from SONALI_MUSIC import app as Sona
from config import OWNER_ID
from SONALI_MUSIC.misc import SUDOERS

mongo_url_pattern = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")
MONGO_DB_URI = os.getenv("MONGO_DB_URI")


ADD_ME_BUTTON = InlineKeyboardMarkup(
    [[InlineKeyboardButton(
        "✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
        url=f"https://t.me/{Sona.username}?startgroup=true"
    )]]
)


@Sona.on_message(filters.command("mongochk"))
async def mongo_command(client, message: Message):

    if len(message.command) < 2:
        await message.reply(
            f"**⋟ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴜʀʟ ᴀꜰᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**\n\n**ᴇxᴀᴍᴘʟᴇ :-** /mongochk mongo_url`",
            reply_markup=ADD_ME_BUTTON
        )
        return

    mongo_url = message.command[1]
    if re.match(mongo_url_pattern, mongo_url):
        try:
            mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            mongo_client.server_info() 
            await message.reply(
                f"**⋟ ᴍᴏɴɢᴏᴅʙ ᴜʀʟ ɪꜱ ᴠᴀʟɪᴅ ᴀɴᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ✅**\n\n**⋟ ᴄʜᴇᴄᴋ ʙʏ :– {Sona.mention}**",
                reply_markup=ADD_ME_BUTTON
            )
        except Exception as e:
            await message.reply(
                f"**⋟ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴍᴏɴɢᴏᴅʙ :-** {e}\n\n**⋟ ᴄʜᴇᴄᴋ ʙʏ :– {Sona.mention}",
                reply_markup=ADD_ME_BUTTON
            )
    else:
        await message.reply(
            f"**⋟ ɪɴᴠᴀʟɪᴅ ᴍᴏɴɢᴏᴅʙ ᴜʀʟ ꜰᴏʀᴍᴀᴛ 💔**\n\n**⋟ ᴄʜᴇᴄᴋ ʙʏ :– {Sona.mention}**",
            reply_markup=ADD_ME_BUTTON
        )


@Sona.on_message(filters.command(["checkdb", "checkdatabase", "hkdb"]) & SUDOERS)
async def check_db_command(client, message: Message):
    ok = await message.reply("**⋟ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴡʜɪʟᴇ ᴄʜᴇᴄᴋɪɴɢ ʏᴏᴜʀ ʙᴏᴛ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ...**")
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()
        result = "**⋟ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇꜱ :-**\n"

        has_user_db = False
        for db_name in databases:
            if db_name not in ["admin", "local"]:
                has_user_db = True
                result += f"\n**{db_name} :-**\n"
                db = mongo_client[db_name]
                for col_name in db.list_collection_names():
                    result += f"  `{col_name}` ({db[col_name].count_documents({})} documents)\n"

        if not has_user_db:
            await ok.delete()
            await message.reply(f"**⋟ ɴᴏ ᴜꜱᴇʀ ᴅᴀᴛᴀʙᴀꜱᴇꜱ ꜰᴏᴜɴᴅ ❌**", reply_markup=ADD_ME_BUTTON)
        elif len(result) > 4096:
            paste_url = await SonaBin(result)
            await ok.delete()
            await message.reply(f"**⋟ ᴅᴀᴛᴀʙᴀꜱᴇ ʟɪꜱᴛ ᴛᴏᴏ ʟᴏɴɢ. ᴠɪᴇᴡ ʜᴇʀᴇ :-** {paste_url}", reply_markup=ADD_ME_BUTTON)
        else:
            await ok.delete()
            await message.reply(result, reply_markup=ADD_ME_BUTTON)

        mongo_client.close()
    except Exception as e:
        await ok.delete()
        await message.reply(f"**⋟ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄʜᴇᴄᴋ ᴅᴀᴛᴀʙᴀꜱᴇ ❌**\n\n**⋟ ᴇʀʀᴏʀ :–** `{e}`", reply_markup=ADD_ME_BUTTON)



def list_dbs_cols(client):
    numbered_list = []
    counter = 1
    for db_name in client.list_database_names():
        if db_name not in ["admin", "local"]:
            numbered_list.append((counter, db_name, None))
            counter += 1
            db = client[db_name]
            for col_name in db.list_collection_names():
                numbered_list.append((counter, db_name, col_name))
                counter += 1
    return numbered_list

def delete_collection(client, db_name, col_name):
    client[db_name].drop_collection(col_name)

def delete_database(client, db_name):
    client.drop_database(db_name)



@Sona.on_message(filters.command(["deletedb", "deletedatabase", "deldb"]) & filters.user(OWNER_ID))
async def delete_db_command(client, message: Message):
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        dbs_cols = list_dbs_cols(mongo_client)

        if len(message.command) == 1:
            result = "**⋟ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇꜱ ᴀɴᴅ ᴄᴏʟʟᴇᴄᴛɪᴏɴꜱ :-**\n"
            for num, db_name, col_name in dbs_cols:
                if col_name:
                    result += f"{num}.) `{col_name}`\n"
                else:
                    result += f"\n{num}.) **{db_name}** (Database)\n"
            await message.reply(result, reply_markup=ADD_ME_BUTTON)
        elif message.command[1].lower() == "all":
            for db_name, col_name in [(d, c) for _, d, c in dbs_cols]:
                if col_name:
                    delete_collection(mongo_client, db_name, col_name)
                else:
                    delete_database(mongo_client, db_name)
            await message.reply("**⋟ ᴀʟʟ ᴅᴀᴛᴀʙᴀꜱᴇꜱ ᴀɴᴅ ᴄᴏʟʟᴇᴄᴛɪᴏɴꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ 🧹**", reply_markup=ADD_ME_BUTTON)
        else:
            await message.reply("**⋟ ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ꜰᴏʀᴍᴀᴛ ❌**", reply_markup=ADD_ME_BUTTON)

        mongo_client.close()
    except Exception as e:
        await message.reply(f"**⋟ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴅᴀᴛᴀʙᴀꜱᴇ ❌**\n\n**⋟ ᴇʀʀᴏʀ :–** `{e}`", reply_markup=ADD_ME_BUTTON)



def backup_mongo(client):
    data = {}
    for db_name in client.list_database_names():
        db = client[db_name]
        data[db_name] = {col: list(db[col].find()) for col in db.list_collection_names()}
    return data

def restore_mongo(client, backup_data):
    for db_name, collections in backup_data.items():
        db = client[db_name]
        for col_name, docs in collections.items():
            if docs:
                db[col_name].insert_many(docs)

@Sona.on_message(filters.command(["transferdb", "copydb"]) & filters.user(OWNER_ID))
async def transfer_db_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply(f"**⋟ ᴘʀᴏᴠɪᴅᴇ ᴛᴀʀɢᴇᴛ ᴍᴏɴɢᴏ ᴜʀʟ ❌**", reply_markup=ADD_ME_BUTTON)
        return
    target_url = message.command[1]
    if not re.match(mongo_url_pattern, target_url):
        await message.reply(f"**⋟ ɪɴᴠᴀʟɪᴅ ᴛᴀʀɢᴇᴛ ᴜʀʟ 💔**", reply_markup=ADD_ME_BUTTON)
        return

    try:
        main_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        backup_data = backup_mongo(main_client)
        main_client.close()

        target_client = MongoClient(target_url, serverSelectionTimeoutMS=5000)
        restore_mongo(target_client, backup_data)
        target_client.close()

        await message.reply("**⋟ ᴅᴀᴛᴀ ᴛʀᴀɴꜱꜰᴇʀ ᴛᴏ ɴᴇᴡ ᴍᴏɴɢᴏ ᴜʀʟ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ✅**", reply_markup=ADD_ME_BUTTON)
    except Exception as e:
        await message.reply(f"**⋟ ᴅᴀᴛᴀ ᴛʀᴀɴꜱꜰᴇʀ ꜰᴀɪʟᴇᴅ ❌**\n\n**⋟ ᴇʀʀᴏʀ :–** `{e}`", reply_markup=ADD_ME_BUTTON)


@Sona.on_message(filters.command(["downloaddata", "owdata"]) & filters.user(OWNER_ID))
async def download_data_command(client, message: Message):
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        data = {}
        for db_name in mongo_client.list_database_names():
            if db_name not in ["admin", "local"]:
                db = mongo_client[db_name]
                data[db_name] = {col: list(db[col].find()) for col in db.list_collection_names()}
        mongo_client.close()

        json_data = json.dumps(data, default=str, indent=2)
        file = io.BytesIO(json_data.encode('utf-8'))
        file.name = "mongo_data.json"
        await client.send_document(chat_id=message.chat.id, document=file)
    except Exception as e:
        await message.reply(f"**⋟ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴅᴀᴛᴀ ❌**\n\n**⋟ ᴇʀʀᴏʀ :–** `{e}`", reply_markup=ADD_ME_BUTTON)
