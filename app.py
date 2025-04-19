from telegram import Bot, Update
from telegram.error import BadRequest

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text.strip()

    if text == "/start":
        bot.send_message(chat_id=chat_id, text="Assalomu alaykum! Menga havolani yuboring, men sizga arabcha so‘zli audiolarni qaytaraman.")
        return 'OK'

    # Yuborilgan linkni chatdan o'chirish
    try:
        bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    except BadRequest as e:
        # Agar xabarni o'chirishda xatolik bo'lsa (masalan, xabar mavjud bo'lmasa), uni e'tiborsiz qoldirish
        print(f"Xatolik: {e}")

    # Excel faylda linkni qidirish
    matched = df[df['Link'] == text]

    if not matched.empty:
        nom = matched.iloc[0]['Nom']
        audio_url = matched.iloc[0]['Link']
        response = requests.get(audio_url)
        audio_file = BytesIO(response.content)
        audio_file.name = 'audio.mp3'
        
        # Audio yuborish va izoh (nom va link)
        bot.send_audio(chat_id=chat_id, audio=audio_file, caption=f"{nom}\n{audio_url}")
    else:
        bot.send_message(chat_id=chat_id, text="Bu havola topilmadi. Iltimos, to‘g‘ri link yuboring.")

    return 'OK'
