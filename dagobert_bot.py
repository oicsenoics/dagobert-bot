import alpaca_trade_api as tradeapi
import os
import sys
import threading
import time
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Dagobert-Bot scannt jetzt den gesamten NASDAQ Breitband!", 200
def run_flask(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# API-Login
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
    STREBER_BUDGET = 15.00
    PUNK_BUDGET = 10.00
    
    # 🔍 DER BREITBAND-STAUBSENSOR: Holt alle aktiven NASDAQ-Aktien
    try:
        all_assets = api.list_assets(status='active', asset_class='us_equity')
        # Wir filtern automatisch die 100 liquidesten Tech-Titel für die Jagd heraus
        breitband_targets = [a.symbol for a in all_assets if a.tradable and a.exchange == 'NASDAQ'][:100]
    except:
        breitband_targets = ["NVDA", "XPEV", "TSM", "BABA", "PLTR", "MARA", "GME"] # Backup-Sicherheit

    # 1. BREITBAND-STREBER-JAGD (Sucht nach dem härtesten Last-Minute-Absacker im gesamten Sektor)
    streber_gekauft = False
    for symbol in breitband_targets:
        if streber_gekauft: break
        try:
            barset = api.get_bars(symbol, '1Min', limit=5).df
            if not barset.empty:
                kurve = barset['close'].tolist()
                if kurve[-1] < (kurve[-3] * 0.993): # Verschärft auf 0.7% fetten Absacker für maximale Rendite!
                    api.submit_order(symbol=symbol, qty=(STREBER_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                    streber_gekauft = True
                    print(f"🔥 BREITBAND-TREFFER STREBER: {symbol} erfolgreich verhaftet!")
        except: pass

    # 2. BREITBAND-PUNK-JAGD (Sucht im gesamten Markt nach der explosivsten Krawall-Aktie)
    punk_gekauft = False
    for symbol in reversed(breitband_targets): # Scannt von der spekulativeren Rückseite der Liste
        if punk_gekauft: break
        try:
            barset = api.get_bars(symbol, '1Min', limit=5).df
            if not barset.empty:
                kurve = barset['close'].tolist()
                if kurve[-1] > (kurve[-2] * 1.005): # Muss in der letzten Minute um 0.5% senkrecht nach oben explodieren!
                    api.submit_order(symbol=symbol, qty=(PUNK_BUDGET/kurve[-1]), side='buy', type='market', time_in_force='day')
                    punk_gekauft = True
                    print(f"⚡ BREITBAND-TREFFER PUNK: {symbol} erfolgreich geschossen!")
        except: pass

while True: time.sleep(3600)
