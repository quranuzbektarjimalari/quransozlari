from flask import Flask, request
import telegram
import os

TOKEN = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM'
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot ishlayapti!'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    bot.send_message(chat_id=chat_id, text=f'Siz yozdingiz: {text}')
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
