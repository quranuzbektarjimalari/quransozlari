import requests

# Botning API kaliti
bot_token = "7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM"

# Render serveringizning URL manzili
webhook_url = "https://quransozlari.onrender.com"

# Webhookni o'rnatish
response = requests.post(f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}")

# Javobni tekshirish
if response.status_code == 200:
    print("Webhook o'rnatildi!")
else:
    print(f"Xatolik yuz berdi! Status Code: {response.status_code}")
