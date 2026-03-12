import os
import logging
import pandas as pd
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Sozlamalar
TOKEN = os.environ.get('TOKEN') 
EXCEL_FILE = 'audio_links.xlsx'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. Excelni yuklash
def load_excel():
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE, header=None)
            df.columns = ['Nom', 'Link']
            return df
        return pd.DataFrame(columns=['Nom', 'Link'])
    except Exception as e:
        print(f"❌ Excel xatosi: {e}")
        return pd.DataFrame(columns=['Nom', 'Link'])

df = load_excel()

# 3. /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Link yuboring, men sizga audio qaytaraman.")

# 4. Xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Xabarni aniqlash (shaxsiy chat yoki kanal post)
    msg = update.message or update.channel_post
    if not msg or not msg.text:
        return

    user_text = msg.text.strip()
    chat_id = msg.chat_id

    # 🛑 MUHIM: Foydalanuvchi yuborgan xabarni (linkni) darhol o'chirish
    try:
        await msg.delete()
    except Exception as e:
        # Agar admin huquqi bo'lmasa yoki xabarni o'chirib bo'lmasa, logda ko'rsatadi
        logging.error(f"Xabarni o'chirishda xato: {e}")

    # Excelda qidirish
    matched = df[df['Link'] == user_text]
    
    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']
        try:
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            audio_file = BytesIO(response.content)
            audio_file.name = f"{nom[:20]}.mp3"
            
            await context.bot.send_audio(
                chat_id=chat_id, 
                audio=audio_file, 
                caption=f"<b>Nomi:</b> {nom}\n<b>Manba:</b> {audio_url}",
                parse_mode="HTML"
            )
            # "Tayyorlanmoqda" xabarini o'chirish
            await status_msg.delete()
        except Exception as e:
            await context.bot.edit_message_text(
                chat_id=chat_id, 
                message_id=status_msg.message_id, 
                text=f"❌ Yuklashda xato: {e}"
            )
    else:
        # Link topilmasa, bot 5 soniyadan keyin o'chib ketadigan xabar yuborishi mumkin
        not_found = await context.bot.send_message(chat_id=chat_id, text="⚠️ Hech narsa topilmadi.")
        # Ixtiyoriy: xatolik xabarini ham 5 soniyadan keyin o'chirib yuborish (chat toza turishi uchun)
        context.job_queue.run_once(lambda c: context.bot.delete_message(chat_id, not_found.message_id), 5)

# 5. Botni ishga tushirish
if __name__ == '__main__':
    if not TOKEN:
        print("❌ TOKEN topilmadi!")
    else:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("🚀 Bot Railway'da linklarni o'chirish rejimi bilan ishga tushdi...")
        application.run_polling()

