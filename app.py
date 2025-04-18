from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os, requests, pandas as pd, nest_asyncio

nest_asyncio.apply()

API_KEY = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM'
AUDIO_FOLDER = 'audio_files'
EXCEL_FILE = 'audio_links.xlsx'

os.makedirs(AUDIO_FOLDER, exist_ok=True)

app = Flask(__name__)
application = Application.builder().token(API_KEY).build()

def get_name_from_excel(link):
    try:
        df = pd.read_excel(EXCEL_FILE)
        match = df[df['Link'] == link]
        return match['Nom'].values[0] if not match.empty else None
    except Exception as e:
        print("Excel xatosi:", e)
        return None

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if not msg.startswith('http'):
        await update.message.reply_text("Audio URL yuboring.")
        return
    name = get_name_from_excel(msg) or "Nom topilmadi"
    try:
        r = requests.get(msg)
        r.raise_for_status()
        path = os.path.join(AUDIO_FOLDER, 'audio.mp3')
        with open(path, 'wb') as f: f.write(r.content)
        await update.message.delete()
        await update.message.reply_audio(audio=open(path, 'rb'), caption=f"{name}\n{msg}")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Audio linkini yuboring.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio))

@app.route(f"/{API_KEY}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.before_first_request
def set_webhook():
    url = f"https://YOUR_RENDER_URL.onrender.com/{API_KEY}"
    requests.get(f"https://api.telegram.org/bot{API_KEY}/setWebhook?url={url}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
