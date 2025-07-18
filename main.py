import threading
import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

def background_worker():
    while True:
        check()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    thread = threading.Thread(target=background_worker, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
