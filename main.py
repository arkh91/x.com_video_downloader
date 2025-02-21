from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# Replace with your bot token
BOT_TOKEN = 'Bot_Token'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome! Send me a Twitter video URL to download it.')

async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    ydl_opts = {
        'format': 'best',  # Download the best quality available
        'outtmpl': '%(id)s.%(ext)s',  # Output file name template
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)  # Clean up the downloaded file
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Message handler for Twitter video URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_twitter_video))

    # Start the bot
    application.run_polling()
