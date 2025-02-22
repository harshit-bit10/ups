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

# 🔹 Sudo Users & Groups (Admins)
SUDO_USERS = {6066102279}  # Replace with actual user IDs
SUDO_GROUPS = {-1002337988665}  # Replace with actual group IDs

logger.info("Bot is starting...")

# ✅ Generate a unique filename
def generate_unique_filename(extension="png") -> str:
    return f"SharkToonsIndia_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.{extension}"

# ✅ Check if user has sudo access
async def is_user_sudo(client, user_id: int) -> bool:
    if user_id in SUDO_USERS:
        return True
    for group_id in SUDO_GROUPS:
        try:
            member = await client.get_chat_member(group_id, user_id)
            if member.status in ["administrator", "creator", "member"]:
                return True
        except Exception:
            pass
    return False

# ✅ Decorator for sudo-only commands
def sudo_only(func):
    async def wrapper(client, message):
        if not await is_user_sudo(client, message.from_user.id):
            await message.reply_text("❌ You don't have permission to use this command.")
            return
        return await func(client, message)
    return wrapper

# 🔥 **Image Upscaling Function (NO AI, NO BLUR, SHARP & NATURAL)**
async def upscale_image_enhanced(img_path: Path) -> Path:
    try:
        img = await asyncio.to_thread(Image.open, img_path)
        img = img.convert("RGB")

        img_cv = np.array(img)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

        height, width = img_cv.shape[:2]

        # ✅ Instead of AI, use high-quality bicubic upscale
        upscaled = await asyncio.to_thread(cv2.resize, img_cv, (width * 4, height * 4), interpolation=cv2.INTER_CUBIC)

        # ✅ Reduce Blur (Balanced Bilateral Filter)
        upscaled = await asyncio.to_thread(cv2.bilateralFilter, upscaled, d=5, sigmaColor=50, sigmaSpace=50)

        # ✅ Slight Contrast Boost for Clarity
        upscaled = cv2.convertScaleAbs(upscaled, alpha=1.05, beta=3)

        # Convert back to PIL
        img_upscaled = Image.fromarray(cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB))

        # ✅ Moderate Sharpness (Natural, No Artificial Look)
        img_upscaled = await asyncio.to_thread(ImageEnhance.Sharpness(img_upscaled).enhance, 20.5)

        # Save upscaled image
        upscaled_path = img_path.parent / generate_unique_filename("png")
        await asyncio.to_thread(img_upscaled.save, upscaled_path)

        return upscaled_path
    except Exception as e:
        logger.error(f"Error in upscaling image: {e}")
        raise Exception("❌ Upscaling failed! Ensure the image is real and supported.")

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

# ✅ Image Processing: Upscale Image
@bot.on_message(filters.photo)
@sudo_only
async def upscale_image(client: Client, message: Message):
    temp_dir = Path(tempfile.mkdtemp())
    img_path = temp_dir / "input.jpg"

    try:
        msg = await message.reply_text("⏳ Downloading image...")
        await message.download(str(img_path))
        await msg.edit_text("🔄 Enhancing image...")

        # Process the image asynchronously
        upscaled_path = await upscale_image_enhanced(img_path)

        await msg.edit_text("✅ Image enhanced successfully! Uploading...")
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

# ✅ Start Bot
logger.info("Bot is running...")
bot.run()
