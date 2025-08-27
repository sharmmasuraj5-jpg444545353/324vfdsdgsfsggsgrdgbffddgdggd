from pyrogram import Client, filters
from faker import Faker
from SONALI_MUSIC import app

fake = Faker()

@app.on_message(filters.command("rand"))
async def generate_info(client, message):  
    # Generate fake data
    name = fake.name()
    address = fake.address()
    country = fake.country()
    phone_number = fake.phone_number()
    email = fake.email()
    city = fake.city()
    state = fake.state()
    zipcode = fake.zipcode()

    info_message = (
        f"**ғᴜʟʟ ηᴧϻє :** {name}\n"
        f"**ᴧᴅᴅʀєss :** {address}\n"
        f"**𝖢σᴜηᴛʀʏ :** {country}\n"
        f"** 𝖯ʜσηє ɴᴜϻʙєʀ :** {phone_number}\n"
        f"**𝖤ϻᴧɪʟ :** {email}\n"
        f"**𝖢ɪᴛʏ :** {city}\n"
        f"**sᴛᴧᴛє :** {state}\n"
        f"**𝖹ɪᴘᴄσᴅє :** {zipcode}"
    )

    await message.reply_text(info_message)  
