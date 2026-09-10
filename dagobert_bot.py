import alpaca_trade_api as tradeapi
import os
import sys
import threading
from flask import Flask

# 🌐 1. DAS ALIBI-FENSTER FÜR RENDER (Kostenloser Web-Service Schutz)
app = Flask(__name__)

@app.route('/')
def home():
    return "Dagobert-Bot läuft im Hintergrund!", 200

def run_flask():
    # Render verlangt standardmäßig den Port 10000
    app.run(host='0.0.0.0', port=10000)

# Startet die Alibi-Webseite in einem eigenen, stummen Hintergrundkanal
threading.Thread(target=run_flask, daemon=True).start()

# 🔑 2. DAS ECHTE HANDELSMODUL
API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
BASE_URL = "https://api.alpaca.markets"

try:
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    konto = api.get_account()
except Exception as e:
    print(f"❌ API-Verbindungsfehler: {e}")
    sys.exit()

STAMM_BUDGET = 100.00
aktuelles_guthaben = float(konto.cash)
klon_faktor = int(aktuelles_guthaben // STAMM_BUDGET)
if klon_faktor < 1: klon_faktor = 1

einsatz_pro_trade = 25.00 * klon_faktor
targets = ["XPEV", "NVDA", "TSM", "BABA"]
print(f"🤖 KLON-ARMEE AKTIVIERTE STUFE: {klon_faktor} (Einsatz: {einsatz_pro_trade:.2f} USD)")

for symbol in targets:
    try:
        barset = api.get_bars(symbol, '1Min', limit=5).df
        if not barset.empty:
            kurve = barset['close'].tolist()
            letzter_kurs = kurve[-1]
            
            if letzter_kurs < (kurve[-3] * 0.995):
                print(f"🔥 ANOMALIE BEI {symbol} ERKANNT!")
                anzahl_aktien = einsatz_pro_trade / letzter_kurs
                
                api.submit_order(
                    symbol=symbol,
                    qty=anzahl_aktien,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
                print(f"✅ ECHTGELD-ORDER GESENDET!")
                break 
    except Exception as e:
        print(f"❌ Fehler bei {symbol}: {e}")

# Hält den Server dauerhaft stumm am Leben
import time
while True:
    time.sleep(3600)

