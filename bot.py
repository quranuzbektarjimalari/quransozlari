import logging
import pandas as pd
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Sozlamalar
TOKEN = os.environ.get('TOKEN') # Railway Variables'dan oladi
EXCEL_FILE = 'audio_links.xlsx'

# Loglarni sozlash (xatolarni ko'rish uchun)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. Excelni yuklash funksiyasi
def load_excel():
    try:
        df = pd.read_excel(EXCEL_FILE, header=None)
        df.columns = ['Nom', 'Link']
        print(f"✅ Excel yuklandi: {len(df)} ta link mavjud.")
        return df
    except Exception as e:
        print(f"❌ Excel xatosi: {e}")
        return pd.DataFrame(columns=['Nom', 'Link'])

df = load_excel()

# 3. /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Link yuboring, men sizga audio qaytaraman.")

# 4. Xabarlarni qayta ishlash (Linkni tekshirish va audio yuborish)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Xabar kanal postimi yoki shaxsiy chatmi aniqlash
    msg = update.message or update.channel_post
    if not msg or not msg.text:
        return

    user_text = msg.text.strip()
    chat_id = msg.chat_id

    # Foydalanuvchi yuborgan linkni o'chirish (ixtiyoriy)
    try:
        await msg.delete()
    except:
        pass

    # Excelda qidirish
    matched = df[df['Link'] == user_text]
    
    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']
        
        status_msg = await context.bot.send_message(chat_id=chat_id, text="🎵 Audio tayyorlanmoqda, kuting...")
        
        try:
            # Audioni yuklab olish
            response = requests.get(audio_url)
            response.raise_for_status()
            audio_file = BytesIO(response.content)
            
            # Audioni yuborish
            await context.bot.send_audio(
                chat_id=chat_id, 
                audio=audio_file, 
                caption=f"<b>Nomi:</b> {nom}\n<b>Link:</b> {audio_url}",
                parse_mode="HTML"
            )
            await status_msg.delete() # "Kuting" xabarini o'chirish
        except Exception as e:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text="❌ Audioni yuborishda xato yuz berdi.")
            print(f"Xato: {e}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Kechirasiz, bu link bazada topilmadi.")

# 5. Botni ishga tushirish
if __name__ == '__main__':
    # Bot ilovasini qurish
    application = Application.builder().token(TOKEN).build()

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🚀 Bot ishga tushdi (Polling)...")
    application.run_polling()

