
import time
import requests
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MESSAGE = os.getenv("MESSAGE")
INTERVAL = int(os.getenv("INTERVAL"))

def send_alert():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": MESSAGE,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Mensaje enviado correctamente.")
    else:
        print("❌ Error al enviar mensaje:", response.text)

if __name__ == "__main__":
    while True:
        send_alert()
        time.sleep(INTERVAL)
