import alpaca_trade_api as tradeapi
import os
import sys
import threading
import time
from flask import Flask

# 🌐 1. DAS ALIBI-FENSTER FÜR RENDER (Kostenloser Web-Service Schutz)
app = Flask(__name__)
@app.route('/')
def home(): return "Dagobert-Bot läuft absolut unzerstörbar!", 200
def run_flask(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# 🔑 2. API-LOGIN
API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
BASE_URL = "https://api.alpaca.markets"

konto = None
try:
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    konto = api.get_account()
    print(f"🏦 Erfolgreich angedockt! Live-Guthaben: {konto.cash} USD")
except Exception as e:
    print(f"⚠️ Verbindung zu Alpaca fehlgeschlagen, versuche es morgen wieder: {e}")

# 📊 3. DIE DOPPEL-STRATEGIE (Wird nur ausgeführt, wenn das Konto erreichbar ist)
if konto is not None:
    STREBER_BUDGET = 15.00
    PUNK_BUDGET = 10.00

    streber_targets = ["XPEV", "NVDA", "TSM", "BABA"]
    punk_targets = ["PLTR", "MARA", "GME"]

    # A. DER STREBER-SCAN (Sucht die gesamte Liste nach der Anomalie ab)
    streber_gekauft = False
    for symbol in streber_targets:
        if streber_gekauft: break
        try:
            barset = api.get_bars(symbol, '1Min', limit=5).df
            if not barset.empty:
                kurve = barset['close'].tolist()
                if kurve[-1] < (kurve[-3] * 0.995): # 0.5% Last-Minute-Absacker
                    api.submit_order(symbol=symbol, qty=(STREBER_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                    streber_gekauft = True
                    print(f"✅ STREBER-ORDER ERFOLGREICH: {symbol} gekauft!")
        except Exception as e:
            print(f"❌ Fehler beim Streber-Scan für {symbol}: {e}")

    # B. DER PUNK-SCAN (Sucht die gesamte Liste nach Krawall-Ausschlägen ab)
    punk_gekauft = False
    for symbol in punk_targets:
        if punk_gekauft: break
        try:
            barset = api.get_bars(symbol, '1Min', limit=5).df
            if not barset.empty:
                kurve = barset['close'].tolist()
                if kurve[-1] > kurve[-2]: # Reiner Aufwärts-Zuckimpuls kurz vor Schluss
                    api.submit_order(symbol=symbol, qty=(PUNK_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                    punk_gekauft = True
                    print(f"✅ PUNK-ORDER ERFOLGREICH: {symbol} gekauft!")
        except Exception as e:
            print(f"❌ Fehler beim Punk-Scan für {symbol}: {e}")

# 🌌 4. DER EWIGE DAUERSCHLAF (Hält den kostenlosen Server online)
while True:
    time.sleep(3600)
