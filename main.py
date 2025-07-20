import os
import time
import threading
import requests
import pytz
from datetime import datetime
from flask import Flask

# Configuración desde variables de entorno
API_KEY = os.environ.get("API_KEY")
CHAT_ID = os.environ.get("CHAT_ID")
INTERVAL = int(os.environ.get("INTERVAL", 900))  # por defecto 900 segundos (15 min)

app = Flask(__name__)

def fetch_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_spain_la_liga/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "totals",
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    if response.ok:
        return response.json()
    else:
        print("Error al obtener cuotas:", response.text, flush=True)
        return []

def fetch_scores():
    url = "https://api.the-odds-api.com/v4/sports/soccer_spain_la_liga/scores/"
    params = {"apiKey": API_KEY}
    response = requests.get(url, params=params)
    if response.ok:
        return response.json()
    else:
        print("Error al obtener resultados:", response.text, flush=True)
        return []

def format_event(event):
    try:
        home = event["home_team"]
        away = event["away_team"]
        commence = event["commence_time"]
        dt = datetime.fromisoformat(commence.replace("Z", "+00:00"))
        madrid_tz = pytz.timezone("Europe/Madrid")
        dt_local = dt.astimezone(madrid_tz)
        fecha = dt_local.strftime("%d/%m/%Y")
        hora = dt_local.strftime("%H:%M")

        book = event["bookmakers"][0]
        odds_data = book["markets"][0]["outcomes"]
        over_25 = next((o for o in odds_data if "Over" in o["name"]), None)
        under_25 = next((o for o in odds_data if "Under" in o["name"]), None)

        cuota_over = over_25["price"] if over_25 else "-"
        cuota_under = under_25["price"] if under_25 else "-"

        return f"📅 {fecha} 🕒 {hora} - {home} vs {away}\n🔥 Over 2.5: {cuota_over} | ❄️ Under 2.5: {cuota_under}"
    except Exception as e:
        print("❌ Error formateando evento:", e, flush=True)
        return None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{API_KEY}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print("❌ Error enviando a Telegram:", response.text, flush=True)
    except Exception as e:
        print("❌ Excepción enviando a Telegram:", e, flush=True)

def check():
    print("🎯 Ejecutando check()", flush=True)
    events = fetch_odds()
    print(f"🎯 Eventos recibidos: {len(events)}", flush=True)

    for ev in events:
        msg = format_event(ev)
        if msg:
            send_telegram(msg)

# Worker en segundo plano
def background_worker():
    iteration = 0
    while True:
        iteration += 1
        print(f"🔁 Iteración #{iteration}", flush=True)
        check()
        time.sleep(INTERVAL)

@app.route("/")
def home():
    return "Bot activo ✅"

# Inicio del bot
if __name__ == "__main__":
    print("🚀 Iniciando bot y servidor Flask...", flush=True)
    thread = threading.Thread(target=background_worker, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
