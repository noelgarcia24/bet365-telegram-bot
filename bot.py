import os
import time
import requests
from flask import Flask

# Configuración
BOT_TOKEN = os.getenv("BOT_TOKEN")  # tu token del bot de Telegram en Render
CHAT_ID = os.getenv("CHAT_ID")      # tu chat id en Render
ODDS_API_KEY = os.getenv("ODDS_API_KEY")  # tu API key de OddsAPI
INTERVAL = 30  # cada 30 segundos para probar

# Flask (para Render uptime)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo ✅"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, json=payload)
        print("📩 Enviado a Telegram:", r.status_code, r.text)
    except Exception as e:
        print("⚠️ Error enviando a Telegram:", e)

def check_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_spain_la_liga/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        response = requests.get(url, params=params)
        print("🔍 Respuesta de OddsAPI:", response.status_code, response.text)  # 👈 DEBUG

        if response.status_code != 200:
            send_telegram_message(f"⚠️ Error API Odds: {response.status_code}")
            return

        data = response.json()
        if not data:
            print("❌ No hay partidos en la respuesta.")
            return

        for match in data:
            home = match["home_team"]
            away = match["away_team"]
            commence = match["commence_time"]

            msg = f"⚽ Partido encontrado:\n{home} vs {away}\n⏰ {commence}"
            send_telegram_message(msg)

    except Exception as e:
        print("⚠️ Error en check_matches:", e)

# Loop infinito (simulación de background worker)
def run_loop():
    while True:
        check_matches()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_loop).start()
    app.run(host="0.0.0.0", port=10000)

