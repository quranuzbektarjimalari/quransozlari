from flask import Flask, request
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

app = Flask(__name__)

# Bot API tokeni
API_KEY = 'your-telegram-bot-api-key'

# Webhook URLni o'rnatish
@app.route(f'/{API_KEY}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str)
    application = Application.builder().token(API_KEY).build()
    application.process_update(update)
    return 'OK', 200

def set_webhook():
    webhook_url = 'https://your-render-app-url.com/' + API_KEY  # Render URL va token
    requests.post(f'https://api.telegram.org/bot{API_KEY}/setWebhook', data={'url': webhook_url})

if __name__ == '__main__':
    set_webhook()  # Webhookni o'rnatish
    app.run(host='0.0.0.0', port=5000)  # Flask serverni ishga tushurish
