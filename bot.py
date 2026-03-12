import os  # <--- Mana shu qator xatoni tuzatadi
import logging
import pandas as pd
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Sozlamalar
# Railway Variables bo'limiga TOKEN deb nomlangan o'zgaruvchi qo'shgan bo'lishingiz shart
TOKEN = os.environ.get('TOKEN') 
EXCEL_FILE = 'audio_links.xlsx'

# Loglarni sozlash
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. Excelni yuklash
def load_excel():
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE, header=None)
            df.columns = ['Nom', 'Link']
            print(f"✅ Excel yuklandi: {len(df)} ta link mavjud.")
            return df
        else:
            print(f"❌ Fayl topilmadi: {EXCEL_FILE}")
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
    msg = update.message or update.channel_post
    if not msg or not msg.text:
        return

    user_text = msg.text.strip()
    chat_id = msg.chat_id

    # Excelda qidirish
    matched = df[df['Link'] == user_text]
    
    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']
        
        status_msg = await context.bot.send_message(chat_id=chat_id, text="🎵 Audio tayyorlanmoqda...")
        
        try:
            response = requests.get(audio_url, timeout=20)
            response.raise_for_status()
            audio_file = BytesIO(response.content)
            audio_file.name = f"{nom[:20]}.mp3"
            
            await context.bot.send_audio(
                chat_id=chat_id, 
                audio=audio_file, 
                caption=f"<b>Nomi:</b> {nom}\n<b>Link:</b> {audio_url}",
                parse_mode="HTML"
            )
            await status_msg.delete()
        except Exception as e:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text=f"❌ Xato: {e}")
    else:
        # Agar link bazada bo'lmasa, bot indamasligi yoki xabar berishi mumkin
        pass

# 5. Botni ishga tushirish
if __name__ == '__main__':
    if not TOKEN:
        print("❌ XATO: TOKEN o'zgaruvchisi topilmadi! Railway Variables'ni tekshiring.")
    else:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("🚀 Bot Railway'da ishga tushdi...")
        application.run_polling()
