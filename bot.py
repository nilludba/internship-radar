import os
import asyncio

from radar import run_all
from dotenv import load_dotenv
from telegram import Update 
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(update.effective_user.id))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await  update.message.reply_text("Hi, i am here to help you find your internship!")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ###Run the radar and send the report
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text("Checking , please wait...")
    report = await asyncio.to_thread(run_all)
    await update.message.reply_text(report[:4000])

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("whoami", whoami))
    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()