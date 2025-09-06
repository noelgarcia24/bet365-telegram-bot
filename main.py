import os
import time
import requests
import threading
from flask import Flask

# =========================
# 🔑 CONFIGURACIÓN
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")       # tu bot token de Telegram
CHAT_ID = os.getenv("CHAT_ID")           # tu chat ID de Telegram
ODDS_API_KEY = os.getenv("ODDS_API_KEY") # tu API key de OddsAPI
INTERVAL = 30                            # cada cuántos segundos consultar
SPORT = "soccer_spain_la_liga"           # LaLiga (puedes cambiarlo)

# =========================
# 🌍 FLASK APP
# =========================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo ✅"

# =========================
# 📩 TELEGRAM
# =========================
def send_telegram_message(message: str):
    """Envía un mensaje a Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, json=payload)
        print("📩 Enviado a Telegram:", r.status_code, r.text)
    except Exception as e:
        print("⚠️ Error enviando a Telegram:", e)

# =========================
# ⚽ CHECK MATCHES
# =========================
def check_matches():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        response = requests.get(url, params=params)
        print("🔍 Respuesta OddsAPI:", response.status_code)

        if response.status_code != 200:
            send_telegram_message(f"⚠️ Error API Odds: {response.status_code}")
            return

        data = response.json()
        if not data:
            print("❌ No hay partidos en la respuesta.")
            return

        for match in data:
            home = match.get("home_team", "Desconocido")
            away = match.get("away_team", "Desconocido")
            commence = match.get("commence_time", "Sin hora")

            msg = f"⚽ Partido encontrado:\n{home} vs {away}\n⏰ {commence}"
            send_telegram_message(msg)

    except Exception as e:
        print("⚠️ Error en check_matches:", e)

# =========================
# 🔄 LOOP EN SEGUNDO PLANO
# =========================
def run_loop():
    while True:
        check_matches()
        time.sleep(INTERVAL)

# =========================
# 🚀 MAIN
# =========================
if __name__ == "__main__":
    # Lanzar loop en un hilo separado
    threading.Thread(target=run_loop, daemon=True).start()
    # Lanzar Flask
    app.run(host="0.0.0.0", port=10000)

