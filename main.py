import asyncio
import tempfile
import shutil
import random
import string
import cv2
import numpy as np
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageEnhance
from loguru import logger

# 🔹 Bot API Credentials
API_ID = 29234663  # Replace with your API ID
API_HASH = "94235bdf61b1b42e67b113b031db5ba5"
BOT_TOKEN = "7219185320:AAE76oh6RBbj0EuUlPNIdVAtIpdeL1K2hfs"

# 🔹 Initialize bot
bot = Client("ImageUpscalerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Task Queue for Sequential Processing
image_queue = asyncio.Queue()


# ✅ Generate a unique filename
def generate_unique_filename(extension="png") -> str:
    return f"SharkToonsIndia_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.{extension}"


# 🔥 Image Upscaling Function (Bicubic, No AI)
async def upscale_image_enhanced(img_path: Path) -> Path:
    try:
        img = await asyncio.to_thread(Image.open, img_path)
        img.verify()  # Validate file type
        img = img.convert("RGB")

        img_cv = np.array(img)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

        height, width = img_cv.shape[:2]

        # ✅ High-quality bicubic upscale
        upscaled = await asyncio.to_thread(cv2.resize, img_cv, (width * 4, height * 4), interpolation=cv2.INTER_CUBIC)

        # ✅ Reduce Blur (Bilateral Filter)
        upscaled = await asyncio.to_thread(cv2.bilateralFilter, upscaled, d=5, sigmaColor=50, sigmaSpace=50)

        # ✅ Slight Contrast Boost
        upscaled = cv2.convertScaleAbs(upscaled, alpha=1.05, beta=3)

        # Convert back to PIL
        img_upscaled = Image.fromarray(cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB))

        # ✅ Moderate Sharpness
        img_upscaled = await asyncio.to_thread(ImageEnhance.Sharpness(img_upscaled).enhance, 20.5)

        # Save upscaled image
        upscaled_path = img_path.parent / generate_unique_filename("png")
        await asyncio.to_thread(img_upscaled.save, upscaled_path)

        return upscaled_path
    except Exception as e:
        logger.error(f"Error in upscaling image: {e}")
        raise Exception("❌ Upscaling failed! Ensure the image is real and supported.")


# ✅ Image Processing Worker (Handles queue one-by-one)
async def process_queue():
    while True:
        client, message = await image_queue.get()
        temp_dir = Path(tempfile.mkdtemp())
        img_path = temp_dir / "input.jpg"

        try:
            msg = await message.reply_text("⏳ Downloading image...")
            await message.download(str(img_path))
            await msg.edit_text("🔄 Enhancing image...")

            # Process image asynchronously
            upscaled_path = await upscale_image_enhanced(img_path)

            await msg.edit_text("✅ Image enhanced! Uploading...")
            await message.reply_document(
                document=str(upscaled_path),
                caption=f"🖼️ Enhanced Image by SharkToonsIndia - {upscaled_path.name}"
            )
            await msg.delete()
        except Exception as e:
            logger.error(f"Processing error: {e}")
            await message.reply_text("❌ Upscaling failed! Ensure the image is real and supported.")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            image_queue.task_done()  # Mark task as complete


# ✅ Command: /start
@bot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_photo(
        photo="https://telegra.ph/Shinobuv3-01-28",
        caption=(
            "<b>✨ Welcome to SharkToonsIndia Bot!</b>\n\n"
            "🚀 Send an image to enhance it!"
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Developer", url="https://t.me/SupremeYoriichi"),
                InlineKeyboardButton("Channel", url="https://t.me/SharkToonsIndia"),
            ],
            [InlineKeyboardButton("Close", callback_data="close")]
        ])
    )


# ✅ Button: Close
@bot.on_callback_query(filters.regex("close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()


# ✅ Image Processing: Add Image to Queue
@bot.on_message(filters.photo)
async def queue_image(client: Client, message: Message):
    await image_queue.put((client, message))  # Add image to queue
    await message.reply_text("🕒 Added to queue! Please wait... Processing in order.")


# ✅ Start Bot with Queue Processor
async def main():
    logger.info("Bot is running...")

    # Start processing queue in background
    asyncio.create_task(process_queue())

    # Start Telegram bot
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
        ..")
bot.run()
