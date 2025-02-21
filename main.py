from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Updater, CallbackContext
import os

# Replace with your bot token
BOT_TOKEN = 'Bot'

# Command 1: Start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome! Send me a Twitter video URL to download it.')

# Command 2: Show some text
async def donation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
CB \\- Tap to Copy
Doge: `DL8t8AQKEkduRkfSziW7hn89zsKFaEbhvJ`

Bitcoin: `36wfr58pdzN8S8kG9sTxQQ3o8rzd1JbVBz`
"""
    await update.message.reply_text(message, parse_mode="MarkdownV2")

# Handle Twitter video URLs
async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
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
        await update.message.reply_text(f"There is an issue with your link: {e}")

# Handle unknown commands
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_commands = """
Available commands:
- /start: Start the bot and get a welcome message.
- /donation: buy me a coffee.
- /help: see all the commands.
"""
    await update.message.reply_text(available_commands)

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("donation", donation))
    #application.add_handler(CommandHandler("showtext", show_text))

    # Message handler for Twitter video URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_twitter_video))

    # Handler for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Start the bot
    application.run_polling()
