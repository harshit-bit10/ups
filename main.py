from pathlib import Path
import asyncio
import tempfile
import shutil
import random
import string
import cv2
import numpy as np
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageEnhance
from loguru import logger

# Bot API Credentials
API_ID = 29234663  # Replace with your API ID
API_HASH = "94235bdf61b1b42e67b113b031db5ba5"
BOT_TOKEN = "7335265361:AAGU69st_vK3kVZIy1lAYSOejGB8EaMgBxQ"

# Initialize bot
bot = Client("ImageUpscalerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logger.info("Bot is starting...")

# Utility function to generate a unique filename
def generate_unique_filename(extension="png") -> str:
    return f"SharkToonsIndia_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.{extension}"

# Image Upscaling and Enhancement
def upscale_and_enhance(img: Image.Image) -> Image.Image:
    try:
        img_cv = np.array(img)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
        height, width = img_cv.shape[:2]
        
        # 4x Upscaling using Super-Resolution
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel("EDSR_x4.pb")  # Use a pre-trained model
        sr.setModel("edsr", 4)  # 4x upscaling
        upscaled = sr.upsample(img_cv)
        
        # Convert back to PIL
        img_upscaled = Image.fromarray(cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB))
        
        # Apply Enhancements
        img_upscaled = ImageEnhance.Sharpness(img_upscaled).enhance(11.5)  # Increase sharpness
        img_upscaled = ImageEnhance.Contrast(img_upscaled).enhance(1.1)  # Increase contrast
        img_upscaled = ImageEnhance.Color(img_upscaled).enhance(1.0)  # Boost colors
        
        return img_upscaled
    except Exception as e:
        logger.error(f"Error in upscaling image: {e}")
        return img  # Return original image if enhancement fails

# Command: /start
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

# Button: Close
@bot.on_callback_query(filters.regex("close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()

# Image Processing: Upscale Image
@bot.on_message(filters.photo)
async def upscale_image(client: Client, message: Message):
    temp_dir = Path(tempfile.mkdtemp())
    img_path = temp_dir / "input.jpg"
    upscaled_path = temp_dir / generate_unique_filename("png")
    
    try:
        msg = await message.reply_text("⏳ Downloading image...")
        await message.download(str(img_path))
        await msg.edit_text("🔄 Enhancing image...")
        
        img = Image.open(img_path).convert("RGB")
        upscaled_img = upscale_and_enhance(img)
        upscaled_img.save(upscaled_path)
        
        await msg.edit_text("✅ Image enhanced successfully! Uploading...")
        await message.reply_document(
            document=str(upscaled_path),
            caption=f"🖼️ Enhanced Image by SharkToonsIndia - {upscaled_path.name}"
        )
        await msg.delete()
    except Exception as e:
        logger.error(f"Processing error: {e}")
        await message.reply_text("❌ An error occurred while processing your image.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# Start Bot
logger.info("Bot is running...")
bot.run()
