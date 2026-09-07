import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import urllib.request
import urllib.parse
from datetime import datetime

# --- SERVEUR WEB HEALTH CHECK POUR RENDER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Lancement du serveur Web en arrière-plan
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- CONFIGURATION IDENTIFIANTS TELEGRAM ---
JETON = "8688412231:AAHe_6a8IzSRpzxAXkxjtYh1T68CfMIvBMU"
ID_CHAT = "87687"  # Assure-toi de remplacer par ton vrai ID Chat si besoin

URL_DE_BASE = f"https://api.telegram.org/bot{JETON}"

def envoyer_signal(message, cible_chat_id=ID_CHAT):
    texte_encode = urllib.parse.quote(message)
    url = f"{URL_DE_BASE}/sendMessage?chat_id={cible_chat_id}&text={texte_encode}&parse_mode=HTML"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("Message envoyé avec succès !")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

def main():
    print("🤖 CryptoRadar Activé")
    envoyer_signal("🚀 CryptoRadar est désormais actif et en ligne 24/7 sur Render !")

if __name__ == "__main__":
    main()
    
    # Boucle infinie pour maintenir le service actif 24/7 sur Render
    while True:
        time.sleep(3600)  # Maintient le processus ouvert
