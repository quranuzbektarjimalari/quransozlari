import os
import requests
import pandas as pd
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
import asyncio

API_KEY = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM'
WEBHOOK_PATH = f"/{API_KEY}"
WEBHOOK_URL = f"https://quransozlari.onrender.com{WEBHOOK_PATH}"

AUDIO_FOLDER = 'audio_files'
EXCEL_FILE = 'audio_links.xlsx'

app = Flask(__name__)
application = Application.builder().token(API_KEY).build()

def get_name_from_excel(link: str):
    try:
        df = pd.read_excel(EXCEL_FILE)
        matching_row = df[df['Link'] == link]
        if not matching_row.empty:
            return matching_row['Nom'].values[0]
    except Exception as e:
        print(f"Excel xatolik: {e}")
    return "Nom topilmadi"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Salom! Audio link yuboring.")

async def download_audio_from_link(update: Update, context: CallbackContext):
    link = update.message.text
    if not link.startswith("http"):
        await update.message.reply_text("Audio link yuboring.")
        return

    audio_name = get_name_from_excel(link)
    try:
        response = requests.get(link)
        response.raise_for_status()
        os.makedirs(AUDIO_FOLDER, exist_ok=True)
        path = os.path.join(AUDIO_FOLDER, "audio.mp3")
        with open(path, "wb") as f:
            f.write(response.content)

        await update.message.delete()
        await update.message.reply_audio(audio=open(path, "rb"), caption=f"{audio_name}\n{link}")

    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio_from_link))

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

@app.route('/')
def home():
    return "Bot Flask orqali ishlayapti."

def set_webhook():
    url = f"https://api.telegram.org/bot{API_KEY}/setWebhook"
    data = {"url": WEBHOOK_URL}
    response = requests.post(url, data=data)
    print("Webhook:", response.text)

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
