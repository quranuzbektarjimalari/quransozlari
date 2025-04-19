from flask import Flask, request
from telegram import Bot, Update
import pandas as pd
import requests
from io import BytesIO

# Bu yerga TOKEN to'g'ridan-to'g'ri yozilgan
TOKEN = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM'
bot = Bot(token=TOKEN)

# Excel faylni yuklash
df = pd.read_excel('audio_links.xlsx', header=None)
df.columns = ['Nom', 'Link']

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot ishga tayyor!'

@app.route('/setwebhook')
def set_webhook():
    webhook_url = f"https://quransozlari.onrender.com/{TOKEN}"
    success = bot.set_webhook(url=webhook_url)
    return "Webhook set: " + str(success)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text.strip()

    if text == "/start":
        bot.send_message(chat_id=chat_id, text="Assalomu alaykum! Menga havolani yuboring, men sizga arabcha so‘zli audiolarni qaytaraman.")
        return 'OK'

    matched = df[df['Link'] == text]

    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']
        response = requests.get(audio_url)
        audio_file = BytesIO(response.content)
        audio_file.name = 'audio.mp3'
        bot.send_audio(chat_id=chat_id, audio=audio_file, caption=nom)
    else:
        bot.send_message(chat_id=chat_id, text="Bu havola topilmadi. Iltimos, to‘g‘ri link yuboring.")

    return 'OK'

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
