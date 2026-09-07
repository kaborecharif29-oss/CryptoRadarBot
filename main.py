import os
import time
import json
import logging
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- SERVEUR WEB HEALTH CHECK (POUR RENDER) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot CryptoRadar active!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- CONFIGURATION BOT TELEGRAM ---
JETON = "8688412231:AAHe_6a8IzSRpzxAXkxjtYh1T68CfMIvBMU"
URL_BASE = f"https://api.telegram.org/bot{JETON}"

def api_request(method, params=None):
    url = f"{URL_BASE}/{method}"
    if params:
        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(url, data=data)
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Erreur API ({method}) : {e}")
        return None

def traiter_message(message_text, chat_id):
    texte = message_text.lower().strip()
    
    if texte in ["/start", "sava", "salut", "hello"]:
        reponse = "🤖 <b>CryptoRadar AI V3 Activé sur le Cloud (24h/24) !</b>\n\nPosez une question ou utilisez les commandes :\n• <code>Analyse le btc</code>\n• <code>Analyse sol 2min</code>"
    elif "analyse" in texte and "btc" in texte:
        reponse = "🔍 <b>CryptoRadar : Observation en cours pour BITCOIN...</b>\n• Analyse dynamique du marché lancée."
    elif "analyse" in texte and "sol" in texte:
        reponse = "🔍 <b>CryptoRadar : Observation en cours pour SOLANA...</b>\n• Analyse dynamique du marché lancée."
    else:
        reponse = "Essayez : <code>Analyse le btc</code> ou <code>Analyse sol 2min</code>"
        
    api_request("sendMessage", {"chat_id": chat_id, "text": reponse, "parse_mode": "HTML"})

def ecouter_messages():
    last_update_id = 0
    print("🤖 CryptoRadar : Écoute des messages activée...")
    while True:
        try:
            updates = api_request("getUpdates", {"offset": last_update_id + 1, "timeout": 30})
            if updates and updates.get("ok"):
                for result in updates.get("result", []):
                    last_update_id = result["update_id"]
                    if "message" in result and "text" in result["message"]:
                        chat_id = result["message"]["chat"]["id"]
                        texte = result["message"]["text"]
                        traiter_message(texte, chat_id)
        except Exception as e:
            print(f"Erreur boucle d'écoute : {e}")
            time.sleep(5)

if __name__ == "__main__":
    ecouter_messages()

