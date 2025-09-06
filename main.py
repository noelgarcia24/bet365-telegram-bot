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

if __name__ == "__main__":
    send_telegram_message("✅ Bot iniciado en Render")
    while True:
        check_matches()
        time.sleep(INTERVAL)
