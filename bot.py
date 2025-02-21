import os
import logging
import asyncio
import tempfile
import shutil
import random
import string
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from realesrgan import RealESRGAN
from PIL import Image

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Bot API credentials
API_ID = int(os.environ.get("API_ID", "29234663"))
API_HASH = os.environ.get("API_HASH", "94235bdf61b1b42e67b113b031db5ba5"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8150798398:AAHdkI-g7U1A32B9IkKyLMvA8wf_dqqvOM")
USE_CUDA = os.environ.get("USE_CUDA", "True") == "True"

# Initialize bot
bot = Client("ImageUpscalerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Load RealESRGAN model
model = RealESRGAN("cuda" if USE_CUDA else "cpu", scale=4)
try:
    model.load_weights("weights/RealESRGAN_x4.pth")
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")


def generate_unique_filename(extension="png"):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"SharkToonsIndia_{random_string}.{extension}"


@bot.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = (
        "<b>✨ Welcome to SharkToonsIndia Bot!</b>\n\n"
        "👋 Send me an image and I will enhance it with AI!\n\n"
        "🚀 <b>Let's get started!</b>\n\n"
        "🔹 Developer: <a href='https://t.me/SupremeYoriichi'>Yoriichi</a>\n"
        "🔹 Channel: <a href='https://t.me/SharkToonsIndia'>SharkToonsIndia</a>"
    )
    inline_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Developer", url="https://t.me/SupremeYoriichi"),
            InlineKeyboardButton("Channel", url="https://t.me/SharkToonsIndia")
        ],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    await message.reply_photo(
        photo="https://telegra.ph/Shinobuv3-01-28",
        caption=welcome_text,
        reply_markup=inline_keyboard
    )


@bot.on_callback_query(filters.regex("close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()


@bot.on_message(filters.photo)
async def upscale_image(client: Client, message: Message):
    temp_dir = tempfile.mkdtemp()
    img_path = os.path.join(temp_dir, "input.jpg")
    upscaled_path = os.path.join(temp_dir, generate_unique_filename("png"))
    try:
        msg = await message.reply_text("⏳ Downloading image...")
        await message.download(img_path)
        await msg.edit_text("🔄 Enhancing the image with AI...")
        
        img = Image.open(img_path).convert("RGB")
        upscaled_img = model.enhance(img)
        upscaled_img.save(upscaled_path)
        
        await msg.edit_text("✅ Image enhanced successfully! Uploading...")
        await message.reply_document(
            document=upscaled_path, 
            caption=f"🖼️ Enhanced Image by SharkToonsIndia - {os.path.basename(upscaled_path)}"
        )
        await msg.delete()
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply_text("❌ An error occurred while processing your image.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


logging.info("Bot is running...")
bot.run()
