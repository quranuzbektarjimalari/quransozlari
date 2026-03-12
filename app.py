from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters
import pandas as pd
import requests
from io import BytesIO
import os

app = Flask(__name__)

TOKEN = os.environ.get('TOKEN')
BASE_WEBHOOK_URL = os.environ.get('BASE_WEBHOOK_URL')

if not TOKEN:
    raise ValueError("❗️ TOKEN environment variable not set.")
if not BASE_WEBHOOK_URL:
    raise ValueError("❗️ BASE_WEBHOOK_URL environment variable not set.")

bot = Bot(token=TOKEN)

# Dispatcher yaratish
dp = Dispatcher(bot, None, workers=0)

# Excel fayl
df = pd.read_excel('audio_links.xlsx', header=None)
df.columns = ['Nom', 'Link']

# Start handler
def start(update: Update, context):
    update.message.reply_text("Assalomu alaykum! Link yuboring, men sizga audio qaytaraman.")

dp.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))

# Flask routes
@app.route('/')
def index():
    return '✅ Railway-da Telegram bot server ishlayapti!'

@app.route('/setwebhook')
def set_webhook():
    webhook_url = f"{BASE_WEBHOOK_URL}/{TOKEN}"
    success = bot.set_webhook(url=webhook_url)
    return f"Webhook o‘rnatildi: {success}"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dp.process_update(update)
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
