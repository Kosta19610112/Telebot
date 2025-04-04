# set_webhook.py
import os
from dotenv import load_dotenv
import telebot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN)

success = bot.set_webhook(url=WEBHOOK_URL)

if success:
    print(f"✅ Webhook установлен на {WEBHOOK_URL}")
else:
    print("❌ Не удалось установить webhook")
