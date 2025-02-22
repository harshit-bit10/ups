from pathlib import Path
import asyncio
import tempfile
import shutil
import random
import string
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from loguru import logger

# Bot API Credentials
API_ID = int("29234663")
API_HASH = "94235bdf61b1b42e67b113b031db5ba5"
BOT_TOKEN = "8150798398:AAHdkI-g7U1A32B9IkKyLMvA8wf_dqqvOM"

# Initialize bot
bot = Client("ImageUpscalerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Sudo Users & Groups
SUDO_USERS = {6066102279}  # Replace with actual user IDs
SUDO_GROUPS = {-1002337988665}  # Replace with actual group IDs

logger.info("Bot is ready...")

# Generate Unique Filename
def generate_unique_filename(extension="png"):
    return f"SharkToonsIndia_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.{extension}"

# Check Sudo Access
async def is_user_sudo(client, user_id):
    if user_id in SUDO_USERS:
        return True
    for group_id in SUDO_GROUPS:
        try:
            await client.get_chat_member(group_id, user_id)
            return True
        except:
            pass
    return False

# Sudo-Only Decorator
def sudo_only(func):
    async def wrapper(client, message):
        if not await is_user_sudo(client, message.from_user.id):
            await message.reply_text("❌ You don't have permission to use this command.")
            return
        return await func(client, message)
    return wrapper

# Basic Image Upscaling (No AI)
def upscale_image_basic(img: Image.Image) -> Image.Image:
    # Convert to OpenCV format
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

    # Resize using bicubic interpolation
    height, width = img_cv.shape[:2]
    new_width, new_height = width * 2, height * 2  # 2x upscale
    upscaled = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    # Convert back to PIL format
    img_upscaled = Image.fromarray(cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB))

    # Enhance sharpness and contrast
    img_upscaled = ImageEnhance.Sharpness(img_upscaled).enhance(1.5)  # Increase sharpness
    img_upscaled = ImageEnhance.Contrast(img_upscaled).enhance(1.2)  # Increase contrast

    return img_upscaled

# Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo="https://telegra.ph/Shinobuv3-01-28",
        caption="<b>✨ Welcome to SharkToonsIndia Bot!</b>\n\n🚀 Send an image to enhance it!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Developer", url="https://t.me/SupremeYoriichi"),
             InlineKeyboardButton("Channel", url="https://t.me/SharkToonsIndia")],
            [InlineKeyboardButton("Close", callback_data="close")]
        ])
    )

# Close Button
@bot.on_callback_query(filters.regex("close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()

# Process Image Upscaling
@bot.on_message(filters.photo)
@sudo_only
async def upscale_image(client: Client, message: Message):
    temp_dir = Path(tempfile.mkdtemp())
    img_path = temp_dir / "input.jpg"
    upscaled_path = temp_dir / generate_unique_filename("png")

    try:
        msg = await message.reply_text("⏳ Downloading image...")
        await message.download(str(img_path))
        await msg.edit_text("🔄 Enhancing image...")

        # Load & Upscale Image
        img = Image.open(img_path).convert("RGB")
        upscaled_img = upscale_image_basic(img)
        upscaled_img.save(upscaled_path)

        await msg.edit_text("✅ Image enhanced successfully! Uploading...")
        await message.reply_document(
            document=str(upscaled_path),
            caption=f"🖼️ Enhanced Image by SharkToonsIndia - {upscaled_path.name}"
        )
        await msg.delete()

    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text("❌ An error occurred while processing your image.")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

logger.info("Bot is running...")
bot.run()
ning...")
bot.run()
    
