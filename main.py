import os
import time
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

INTERVAL = 60  # cada 60s revisar partidos

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, json=payload)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Error enviando a Telegram:", e)

def check_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_spain_la_liga/odds/"
    params = {"apiKey": ODDS_API_KEY, "regions": "eu"}
    try:
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print("Error API Odds:", r.text)
            return
        data = r.json()
        if not data:
            print("No hay partidos disponibles")
            return
        for match in data[:3]:  # solo primeros 3 para pruebas
            home = match['home_team']
            away = match['away_team']
            msg = f"Partido detectado: {home} vs {away}"
            send_telegram_message(msg)
    except Exception as e:
        print("Error en check_matches:", e)

@app.route("/")
def home():
    return "Bot activo!"

import os
import requests
import sys

# 🔹 Al arrancar, escribe un log para Render
print("🚀 main.py se ha cargado correctamente", file=sys.stderr)

# 🔹 Intenta mandar un mensaje de prueba a Telegram
try:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": "🚀 Bot en Render arrancado con éxito"}
        r = requests.post(url, data=data)
        print(f"✅ Mensaje enviado a Telegram, status {r.status_code}", file=sys.stderr)
    else:
        print("⚠️ Falta TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en variables de entorno", file=sys.stderr)

except Exception as e:
    print(f"❌ Error enviando mensaje de prueba: {e}", file=sys.stderr)


if __name__ == "__main__":
    send_telegram_message("✅ Bot iniciado en Render")
    while True:
        check_matches()
        time.sleep(INTERVAL)
