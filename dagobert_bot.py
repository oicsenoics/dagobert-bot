import alpaca_trade_api as tradeapi
import os
import sys
import threading
import time
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Dagobert-Bot läuft mit Kurs-Punks!", 200
def run_flask(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# API-Login
API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
BASE_URL = "https://api.alpaca.markets"

try:
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    konto = api.get_account()
except Exception as e:
    sys.exit()

# DIE NEUE DOPPEL-STRATEGIE (FÜRS WOCHENENDE VORBEREITET)
STREBER_BUDGET = 15.00
PUNK_BUDGET = 10.00

streber_targets = ["XPEV", "NVDA", "TSM", "BABA"]
punk_targets = ["PLTR", "MARA", "GME"]

# 1. DER STREBER-SCAN (Sture Anomalie-Jagd)
for symbol in streber_targets:
    try:
        barset = api.get_bars(symbol, '1Min', limit=5).df
        if not barset.empty:
            kurve = barset['close'].tolist()
            if kurve[-1] < (kurve[-3] * 0.995): # Harter Absacker
                api.submit_order(symbol=symbol, qty=(STREBER_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                break
    except: pass

# 2. DER PUNK-SCAN (Erhöhte Action kurz vor Schluss!)
for symbol in punk_targets:
    try:
        barset = api.get_bars(symbol, '1Min', limit=5).df
        if not barset.empty:
            kurve = barset['close'].tolist()
            # Punks brauchen weniger Hürden: Wenn die Aktie in den letzten 2 Min einfach nur im Aufwärtstrend zuckt, springt der Bot auf!
            if kurve[-1] > kurve[-2]:
                api.submit_order(symbol=symbol, qty=(PUNK_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                break
    except: pass

while True: time.sleep(3600)
