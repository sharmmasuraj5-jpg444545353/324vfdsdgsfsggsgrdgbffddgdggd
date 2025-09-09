import os
import cv2
from PIL import Image
from pyrogram import filters
from SONALI_MUSIC import app
from lottie.importers.tgs import import_tgs
from lottie.exporters.tgs import export_tgs


@app.on_message(filters.command("tiny"))
async def tiny_sticker(client, message):
    reply = message.reply_to_message
    if not (reply and reply.sticker):
        await message.reply("⚠️ Reply to a sticker first.")
        return

    kontol = await message.reply("⏳ Processing...")
    ik = await app.download_media(reply)
    im1 = Image.open("SONALI_MUSIC/assets/shashank.png")

    # For animated stickers (.tgs)
    if ik.endswith(".tgs"):
        with open(ik, "rb") as f:
            animation = import_tgs(f)

        # shrink size (tiny)
        animation.width = 200
        animation.height = 200

        file = "tiny.tgs"
        with open(file, "wb") as f:
            export_tgs(animation, f)

    # For video/gif stickers
    elif ik.endswith((".gif", ".mp4")):
        iik = cv2.VideoCapture(ik)
        _, busy = iik.read()
        cv2.imwrite("i.png", busy)
        fil = "i.png"

        im = Image.open(fil)
        z, d = im.size
        xxx, yyy = (200, 200) if z == d else (200, int(200 * d / z))
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)

        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"

        os.remove(fil)
        os.remove("k.png")

    # For normal static stickers
    else:
        im = Image.open(ik)
        z, d = im.size
        xxx, yyy = (200, 200) if z == d else (200, int(200 * d / z))
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)

        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"

        os.remove("k.png")

    # Send final sticker
    await message.reply_sticker(file)
    await kontol.delete()

    # cleanup
    os.remove(file)
    os.remove(ik)
