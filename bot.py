import time
import requests
import json
import pytz
from datetime import datetime
from flask import Flask
import threading

# Flask app para mantener vivo el bot
app = Flask(__name__)

@app.route('/')
def ping():
    return "I'm alive!"

# Cargar configuración desde variables de entorno simuladas (Render usaría reales)
with open("config.json") as f:
    cfg = json.load(f)

API_KEY = cfg["api_key"]
TOKEN = cfg["token"]
CHAT_ID = cfg["chat_id"]
INTERVAL = cfg["interval_seconds"]
SPORT = "soccer_spain_la_liga"
REGION = "eu"
MARKETS = ["spreads", "totals"]
last = {}

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data)
        print("✅ Enviado" if r.status_code == 200 else f"❌ {r.text}")
    except Exception as e:
        print("❌ Error al enviar:", e)

def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "regions": REGION,
        "markets": ",".join(MARKETS),
        "oddsFormat": "decimal",
        "apiKey": API_KEY
    }
    r = requests.get(url, params=params)
    return r.json() if r.ok else []

def fetch_scores(event_ids):
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/scores"
    params = {"apiKey": API_KEY, "eventIds": ",".join(event_ids)}
    r = requests.get(url, params=params)
    return {e["id"]: e for e in r.json()} if r.ok else {}

def check():
    evs = fetch_odds()
    print(f"\n🎯 Eventos recibidos: {len(evs)}")
    tz = pytz.timezone("Europe/Madrid")
    scores_map = fetch_scores([e["id"] for e in evs])

    for event in evs:
        match = event["home_team"] + " vs " + event["away_team"]
        utc = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
        start_time = utc.astimezone(tz).strftime("%d/%m %H:%M")

        info = scores_map.get(event["id"])
        if info and info.get("scores"):
            scores = {p["name"]: p["score"] for p in info["scores"]}
            live = f"⏱️ En juego: {scores.get(event['home_team'], 0)}–{scores.get(event['away_team'], 0)}"
        else:
            live = f"🕰️ {start_time}"

        preferred = event["bookmakers"][0] if event["bookmakers"] else None
        if not preferred:
            continue

        msg_lines = []
        for m in preferred["markets"]:
            mkey = m["key"]
            if mkey not in ("spreads", "totals"):
                continue

            market_type = "Asian Handicap" if mkey == "spreads" else "Over/Under"
            for o in m["outcomes"]:
                label = o["name"]
                price = o["price"]
                point = o.get("point")
                if point is not None:
                    label = f"{label} {point}"

                key = f"{market_type} | {label}"
                prev = last.get(match, {}).get(key)
                icon = "🆕"
                if prev is not None:
                    if abs(prev - price) >= 0.10:
                        icon = "🔼" if price > prev else "🔽"
                        line = f"{market_type}: {label} @ {price} {icon} desde {prev}"
                    else:
                        continue
                else:
                    line = f"{market_type}: {label} @ {price} {icon}"

                print(f"🔔 {line}")
                msg_lines.append(line)
                last.setdefault(match, {})[key] = price

        if msg_lines:
            full_msg = f"<b>{match}</b>\n📍 <i>Bookmaker:</i> {preferred['title']}\n{live}\n\n" + "\n".join(msg_lines)
            print("📤 ENVIANDO:", full_msg)
            send_alert(full_msg)

# Iniciar Flask + chequeo periódico
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    while True:
        check()
        time.sleep(INTERVAL)
