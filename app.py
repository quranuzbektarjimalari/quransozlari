from flask import Flask, request
import telegram
import pandas as pd
import requests
from io import BytesIO

TOKEN = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM'
bot = telegram.Bot(token=TOKEN)

# Excel faylni yuklash
df = pd.read_excel('audio_links.xlsx', header=None)
df.columns = ['Nom', 'Link']  # Ustun nomlari qo‘shiladi

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot ishga tayyor!'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text.strip()

    # Link bo‘yicha qidiruv
    matched = df[df['Link'] == text]

    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']

        # Audioni yuklash
        response = requests.get(audio_url)
        audio_file = BytesIO(response.content)
        audio_file.name = 'audio.mp3'

        # Audio yuborish + caption (arabcha so‘z)
        bot.send_audio(chat_id=chat_id, audio=audio_file, caption=nom)
    else:
        bot.send_message(chat_id=chat_id, text="Bu havola topilmadi. Iltimos, to‘g‘ri link yuboring.")

    return 'OK'

# Gunicorn serveri ishga tushiriladi
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
