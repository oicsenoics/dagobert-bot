import alpaca_trade_api as tradeapi
import os
import sys
import threading
import time
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Dagobert-Bot ist im absoluten Red Alert Modus!", 200
def run_flask(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# API-Login (Mit dem lebenswichtigen "api.")
API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
BASE_URL = "https://api.alpaca.markets"

konto = None
try:
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    konto = api.get_account()
except Exception as e:
    sys.exit()

if konto is not None:
    GESAMT_BUDGET = 25.00 # Die 25 Mücken fliegen komplett in ein einziges Ziel!
    
    try:
        all_assets = api.list_assets(status='active', asset_class='us_equity')
        breitband_targets = [a.symbol for a in all_assets if a.tradable and a.exchange == 'NASDAQ'][:100]
    except:
        breitband_targets = ["NVDA", "XPEV", "TSM", "PLTR"]

    trade_ausgefuehrt = False
    
    # 🔍 SCHRITT 1: Der sensible Scan
    for symbol in breitband_targets:
        if trade_ausgefuehrt: break
        try:
            barset = api.get_bars(symbol, '1Min', limit=5).df
            if not barset.empty:
                kurve = barset['close'].tolist()
                # Sensible Masche: Jeder kleine Ruckler nach unten reicht!
                if kurve[-1] < kurve[-2]:
                    api.submit_order(symbol=symbol, qty=(GESAMT_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                    print(f"🔥 BLOCKBUSTER: {symbol} im regulären Scan erwischt!")
                    trade_ausgefuehrt = True
        except: pass

    # 🚨 SCHRITT 2: DER ABSOLUTE RED ALERT ERZWINGUNGS-MUTATION-HEBEL
    # Wenn bis hierhin absolut gar nichts passiert ist, greift die Brechstange!
    if not trade_ausgefuehrt:
        for symbol in breitband_targets:
            try:
                # Holt den allerletzten verfügbaren Kurs und drückt blind ab!
                barset = api.get_bars(symbol, '1Min', limit=1).df
                if not barset.empty:
                    letzter_kurs = barset['close'].tolist()[-1]
                    api.submit_order(symbol=symbol, qty=(GESAMT_BUDGET/letzter_kurs), side='buy', type='market', time_in_force='day')
                    print(f"🚨 ERZWUNGENER COMBAT-TRADE: {symbol} blind verhaftet!")
                    trade_ausgefuehrt = True
                    break
            except: pass

while True: time.sleep(3600)
