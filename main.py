import logging
import os
import asyncio
from datetime import datetime
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError

# Replace with your bot token
BOT_TOKEN = 'Bot'

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def print_timestamp():
    """Prints the current time in the format mmddyyyy - hhmmss."""
    now = datetime.now()
    timestamp = now.strftime("%m%d%Y - %H%M%S")
    print(f"[{timestamp}]")

# Command 1: Start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome! Send me a Twitter video URL to download it.')

# Command 2: Show donation information
async def donation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
CB \\- Tap to Copy
Doge: `DL8t8AQKEkduRkfSziW7hn89zsKFaEbhvJ`

Bitcoin: `36wfr58pdzN8S8kG9sTxQQ3o8rzd1JbVBz`
"""
    await update.message.reply_text(message, parse_mode="MarkdownV2")

# Command 3: Show about information
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
Welcome to the X.com Video Downloader Bot!

This bot allows you to easily download videos from X.com (formerly known as Twitter by /start). Simply send the URL of the video you want to download, and the bot will process the request and provide you the video.

If you enjoy using this bot and want to support its development, consider making a donation. Your support helps keep the bot running smoothly and allows for future improvements.

To donate, use the command: /donation

Thank you for your support! 🎉
"""
    await update.message.reply_text(message)

# Handle Twitter video URLs
async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print_timestamp()
    url = update.message.text

    # Validate the URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            await update.message.reply_text("Invalid URL format. Please provide a valid URL.")
            return
    except Exception as e:
        await update.message.reply_text(f"Invalid URL: {e}")
        return

    ydl_opts = {
        'format': 'best',  # Download the best quality available
        'outtmpl': '%(id)s.%(ext)s',  # Output file name template
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            await update.message.reply_text("Please wait while the video is being downloaded!")
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)  # Clean up the downloaded file
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await update.message.reply_text(f"There is an issue with your link: {e}")
    print("----------------------------------------------------------------------------")

# Handle unknown commands
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_commands = """
Available commands:
- /start: Start the bot and get a welcome message.
- /donation: Buy me a coffee.
- /about: Learn more about the bot.
"""
    await update.message.reply_text(available_commands)

# Retry mechanism for network errors
async def retry_request(func, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            return await func()
        except NetworkError as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("donation", donation))
    application.add_handler(CommandHandler("about", about))

    # Message handler for Twitter video URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_twitter_video))

    # Handler for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Start the bot with retry mechanism
    try:
        await application.initialize()  # Initialize the application
        await application.start()  # Start the application
        await application.updater.start_polling()  # Start polling for updates
        await asyncio.Event().wait()  # Keep the bot running
    except Exception as e:
        logger.error(f"Application failed: {e}")
    finally:
        await application.stop()  # Stop the application
        await application.shutdown()  # Shut down the application

if __name__ == "__main__":
    asyncio.run(main())
