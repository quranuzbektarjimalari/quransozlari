from flask import Flask, request
from telegram import Bot, Update
import pandas as pd
import requests
from io import BytesIO

# TOKEN
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
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)

    chat_id = None
    text = None
    message_id = None

    # Shaxsiy chat
    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text.strip() if update.message.text else None
        message_id = update.message.message_id

        if text == "/start":
            bot.send_message(chat_id=chat_id, text="Assalomu alaykum! Link yuboring, men sizga audio qaytaraman.")
            return 'OK'

    # Kanal xabari
    elif update.channel_post:
        chat_id = update.channel_post.chat.id
        text = update.channel_post.text.strip() if update.channel_post.text else None
        message_id = update.channel_post.message_id

    # Agar text yoki chat_id yo'q bo'lsa, tugatamiz
    if not text or not chat_id:
        return 'OK'

    # Xabarni o'chirishga urinish (shaxsiy yoki kanal)
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass  # Xatolik bo‘lsa (masalan, kanalga ruxsat yo‘q), davom etadi

    # Exceldan linkni qidirish
    matched = df[df['Link'] == text]
    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']
        response = requests.get(audio_url)
        audio_file = BytesIO(response.content)
        audio_file.name = 'audio.mp3'
        caption = f"{nom}\n{audio_url}"
        bot.send_audio(chat_id=chat_id, audio=audio_file, caption=caption)
    else:
        bot.send_message(chat_id=chat_id, text="Bu link topilmadi. Iltimos, to‘g‘ri link yuboring.")

    return 'OK'

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
