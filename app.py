from flask import Flask, request
from telegram import Bot, Update
import pandas as pd
import requests
from io import BytesIO
import os

# ✅ Flask ilovasi
app = Flask(__name__)

# ✅ Environment variables
TOKEN = os.environ.get('TOKEN')
BASE_WEBHOOK_URL = os.environ.get('BASE_WEBHOOK_URL')

if not TOKEN:
    raise ValueError("❗️ Environment variable 'TOKEN' is not set.")
if not BASE_WEBHOOK_URL:
    raise ValueError("❗️ Environment variable 'BASE_WEBHOOK_URL' is not set.")

bot = Bot(token=TOKEN)

# ✅ Excel faylni ochish
try:
    df = pd.read_excel('audio_links.xlsx', header=None)
    df.columns = ['Nom', 'Link']
    print(f"✅ Excel yuklandi. {len(df)} ta yozuv topildi.")
except Exception as e:
    print(f"❗️ Excel faylni ochishda xato: {e}")
    df = pd.DataFrame(columns=['Nom', 'Link'])

# ✅ Index
@app.route('/')
def index():
    return '✅ Bot ishga tushdi!'

# ✅ /setwebhook route
@app.route('/setwebhook')
def set_webhook():
    webhook_url = f"{BASE_WEBHOOK_URL}/{TOKEN}"
    try:
        success = bot.set_webhook(url=webhook_url)
        return f"✅ Webhook set: {success}\nURL: {webhook_url}"
    except Exception as e:
        return f"❗️ Webhook o'rnatishda xato: {e}"

# ✅ Webhook listener
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
            bot.send_message(
                chat_id=chat_id,
                text="Assalomu alaykum! Link yuboring, men sizga audio qaytaraman."
            )
            return 'OK'

    # Kanal post
    elif update.channel_post:
        chat_id = update.channel_post.chat.id
        text = update.channel_post.text.strip() if update.channel_post.text else None
        message_id = update.channel_post.message_id

    if not text or not chat_id:
        return 'OK'

    # Xabarni o'chirishga urinish
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"❗️ Xabarni o'chirishda xato: {e}")

    # Excelda qidirish
    matched = df[df['Link'] == text]
    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']

        try:
            response = requests.get(audio_url)
            response.raise_for_status()

            audio_file = BytesIO(response.content)
            audio_file.name = 'audio.mp3'

            caption = f"{nom}\n{audio_url}"
            bot.send_audio(chat_id=chat_id, audio=audio_file, caption=caption)
        except Exception as e:
            print(f"❗️ Audio yuklashda xato: {e}")
            bot.send_message(chat_id=chat_id, text="Audio faylni yuklashda muammo bo'ldi.")
    else:
        bot.send_message(chat_id=chat_id, text="❗️ Bu link topilmadi. Iltimos, to‘g‘ri link yuboring.")

    return 'OK'

# ✅ Flaskni ishga tushurish
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
