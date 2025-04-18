import os
import requests
import pandas as pd
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

API_KEY = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM'  # Bot tokeningizni shu yerga qo'shdim
AUDIO_FOLDER = 'audio_files'
EXCEL_FILE = 'audio_links.xlsx'

app = Flask(__name__)
telegram_app = Application.builder().token(API_KEY).build()

if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

def get_name_from_excel(link: str):
    try:
        df = pd.read_excel(EXCEL_FILE)
        matching_row = df[df['Link'] == link]
        if not matching_row.empty:
            return matching_row['Nom'].values[0]
        else:
            return None
    except Exception as e:
        print(f"Excel o'qishda xatolik: {str(e)}")
        return None

async def download_audio_from_link(update: Update, context: CallbackContext):
    message_text = update.message.text
    if not message_text.startswith('http'):
        await update.message.reply_text("Iltimos, audio faylning URL manzilini yuboring.")
        return

    audio_name = get_name_from_excel(message_text) or "Nom topilmadi"
    try:
        response = requests.get(message_text)
        response.raise_for_status()
        audio_file_path = os.path.join(AUDIO_FOLDER, 'audio.mp3')
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)
        await update.message.delete()
        caption = f"{audio_name}\n {message_text}"
        await update.message.reply_audio(audio=open(audio_file_path, 'rb'), caption=caption)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Faylni olishda xatolik: {str(e)}")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Salom! Audio linkini yuboring, men uni sizga fayl sifatida yuboraman.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio_from_link))

@app.route(f'/{API_KEY}', methods=['POST'])
def webhook():
    # Webhookdan kelgan so'rovni qabul qilish
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return 'OK'

@app.route('/')
def index():
    return "Bot ishlayapti!"

if __name__ == '__main__':
    # Flask serverini ishga tushurish
    app.run(debug=True, host='0.0.0.0', port=5000)
