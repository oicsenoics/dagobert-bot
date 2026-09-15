import alpaca_trade_api as tradeapi
import os
import sys
import threading
import time
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Dagobert-Bot jagt jetzt ohne Bremsen!", 200
def run_flask(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# API-Login (Zieht die Schlüssel sicher aus dem Render-Tresor)
API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
BASE_URL = "https://api.alpaca.markets"

try:
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    konto = api.get_account()
except Exception as e:
    sys.exit()

# DIE DOPPEL-STRATEGIE (Ohne Schleifen-Blockaden!)
STREBER_BUDGET = 15.00
PUNK_BUDGET = 10.00

streber_targets = ["XPEV", "NVDA", "TSM", "BABA"]
punk_targets = ["PLTR", "MARA", "GME"]

# 1. DER STREBER-SCAN (Sucht die gesamte Liste nach der Anomalie ab)
streber_gekauft = False
for symbol in streber_targets:
    if streber_gekauft: break  # Stoppt erst, WENN heute wirklich schon ein Streber gekauft wurde
    try:
        barset = api.get_bars(symbol, '1Min', limit=5).df
        if not barset.empty:
            kurve = barset['close'].tolist()
            if kurve[-1] < (kurve[-3] * 0.995): # 0.5% Last-Minute-Absacker
                api.submit_order(symbol=symbol, qty=(STREBER_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                streber_gekauft = True
    except: pass

# 2. DER PUNK-SCAN (Sucht die gesamte Liste nach Krawall-Ausschlägen ab)
punk_gekauft = False
for symbol in punk_targets:
    if punk_gekauft: break  # Stoppt erst, WENN heute wirklich schon ein Punk gekauft wurde
    try:
        barset = api.get_bars(symbol, '1Min', limit=5).df
        if not barset.empty:
            kurve = barset['close'].tolist()
            if kurve[-1] > kurve[-2]: # Reiner Aufwärts-Zuckimpuls kurz vor Schluss
                api.submit_order(symbol=symbol, qty=(PUNK_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                punk_gekauft = True
    except: pass

while True: time.sleep(3600)
