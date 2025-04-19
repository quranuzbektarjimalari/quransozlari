from flask import Flask, request
from telegram import Bot, Update
import pandas as pd
import requests
from io import BytesIO
import os

TOKEN = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM'
bot = Bot(token=TOKEN)

# Excel faylni yuklash
df = pd.read_excel('audio_links.xlsx', header=None)
df.columns = ['Nom', 'Link']

app = Flask(__name__)

# 🧠 Bot ishga tushganda webhook avtomatik o‘rnatiladi
@app.before_first_request
def activate_webhook():
    webhook_url = f"https://quransozlari.onrender.com/{TOKEN}"
    bot.set_webhook(url=webhook_url)

@app.route('/')
def index():
    return 'Bot ishga tayyor!'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    message = update.message
    chat_id = message.chat.id
    text = message.text.strip()

    # 🧹 Foydalanuvchi yuborgan linkni o‘chirish
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    except:
        pass  # xatolik bo‘lsa, davom etadi

    # ✅ /start buyrug‘i
    if text == "/start":
        bot.send_message(
            chat_id=chat_id,
            text="Assalomu alaykum!\nMenga audio havolasini yuboring.\nMen sizga mos audio faylni va maʼlumotini qaytaraman."
        )
        return 'OK'

    # 🔎 Linkni Excel fayldan qidirish
    matched = df[df['Link'] == text]

    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']

        # 🔊 Audio faylni olish
        response = requests.get(audio_url)
        audio_file = BytesIO(response.content)
        audio_file.name = 'audio.mp3'

        # 📩 Audio yuborish (nom + link izohda)
        caption = f"{nom}\n{audio_url}"
        bot.send_audio(chat_id=chat_id, audio=audio_file, caption=caption)
    else:
        bot.send_message(chat_id=chat_id, text="❗️Bu link topilmadi. Iltimos, to‘g‘ri havola yuboring.")

    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
