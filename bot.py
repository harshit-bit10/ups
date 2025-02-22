from pathlib import Path
import asyncio
import tempfile
import shutil
import random
import string
import numpy as np
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
from loguru import logger
from super_image import EdsrModel, ImageLoader

# Bot API Credentials
API_ID = int("29234663")
API_HASH = "94235bdf61b1b42e67b113b031db5ba5"
BOT_TOKEN = "8150798398:AAHdkI-g7U1A32B9IkKyLMvA8wf_dqqvOM"

# Initialize bot
bot = Client("ImageUpscalerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Sudo Users & Groups
SUDO_USERS = {6066102279}  # Replace with actual user IDs
SUDO_GROUPS = {-1002337988665}  # Replace with actual group IDs

# Load AI Upscaler Model
logger.info("Loading AI upscaler model...")
model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=4)  # Uses EDSR model
logger.success("Model loaded successfully.")

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

# Upscale Image using `super-image`
def upscale_image_super(img: Image.Image) -> Image.Image:
    return ImageLoader(model)(img)  # Automatically applies AI enhancement

# Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo="https://telegra.ph/Shinobuv3-01-28",
        caption="<b>✨ Welcome to SharkToonsIndia Bot!</b>\n\n🚀 Send an image to enhance it with AI!",
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
        await msg.edit_text("🔄 Enhancing image with AI...")

        # Load & Upscale Image
        img = Image.open(img_path).convert("RGB")
        upscaled_img = upscale_image_super(img)
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
    
