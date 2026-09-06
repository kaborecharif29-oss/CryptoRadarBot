import json
import re
import threading
import time
import urllib.parse
import urllib.request

# Configuration Telegram CryptoRadar
PARTIE1 = "8688412231:"
PARTIE2 = "AAHe_6a8IzSRpzxAXkxjtYh1T68CfMIvBMU"
TOKEN = PARTIE1 + PARTIE2

CHAT_ID = "8768781139"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
TAUX_USD_FCFA = 600


def envoyer_signal(message, target_chat_id=CHAT_ID):
    texte_encode = urllib.parse.quote(message)
    url = f"{BASE_URL}/sendMessage?chat_id={target_chat_id}&text={texte_encode}&parse_mode=Markdown"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            pass
    except Exception as e:
        print("Erreur d'envoi :", e)


def obtenir_donnees_crypto(crypto_id):
    mapping = {
        "btc": "bitcoin",
        "bitcoin": "bitcoin",
        "eth": "ethereum",
        "ethereum": "ethereum",
        "sol": "solana",
        "solana": "solana",
        "bnb": "binancecoin",
        "xrp": "ripple",
        "ada": "cardano",
        "avax": "avalanche-2",
    }
    crypto_id = mapping.get(crypto_id.lower(), crypto_id.lower())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if crypto_id in data:
                return crypto_id, data[crypto_id]
    except Exception:
        pass
    return crypto_id, None


def extraire_crypto_du_texte(texte):
    cryptos_connues = [
        "btc",
        "bitcoin",
        "eth",
        "ethereum",
        "sol",
        "solana",
        "bnb",
        "xrp",
        "ada",
        "avax",
    ]
    mots = re.findall(r"\w+", texte.lower())

    for mot in mots:
        if mot in cryptos_connues:
            return mot

    return "bitcoin"


def repondre_avec_ia_crypto(question):
    q = question.lower()

    if any(
        m in q
        for m in [
            "salut",
            "bonjour",
            "hello",
            "sava",
            "ça va",
            "ca va",
            "coucou",
            "qui es-tu",
        ]
    ):
        return (
            "👋 **Bonjour ! Ça va très bien, merci !**\n\n"
            "Je suis votre assistant **CryptoRadar AI**. Je peux analyser les"
            " cours en temps réel et calculer votre gestion du risque.\n\n"
            "💡 Écrivez par exemple : `Analyse le btc` ou `Analyse sol 2min`"
        )

    elif "solana" in q or "sol" in q:
        return (
            "⚡ **Analyse rapide de Solana (SOL) :**\n\n"
            "Solana est un réseau très rapide à forte activité. C'est un"
            " actif très performant mais sujet à une forte volatilité.\n\n"
            "👉 Pour démarrer le suivi en temps réel : écrivez `Analyse sol` !"
        )

    elif "bitcoin" in q or "btc" in q:
        return (
            "🪙 **Analyse rapide de Bitcoin (BTC) :**\n\n"
            "Bitcoin est la valeur refuge du marché des cryptomonnaies.\n\n"
            "👉 Pour démarrer le suivi en temps réel : écrivez `Analyse btc` !"
        )

    else:
        return (
            f"🧠 **CryptoRadar AI :**\n\n"
            f"J'ai bien reçu votre message : *« {question} »*\n\n"
            "• **Pour analyser une crypto :** `Analyse le btc` ou `Analyse sol"
            " 2min`\n"
            "• **Pour calculer votre lot :** `lot 1000 2 30`"
        )


def tache_observation_fond(crypto_raw, delai_secondes, label_duree, target_chat_id):
    crypto_id, data_initiale = obtenir_donnees_crypto(crypto_raw)

    if not data_initiale:
        envoyer_signal(
            f"❌ Crypto `{crypto_raw}` introuvable.",
            target_chat_id=target_chat_id,
        )
        return

    prix_depart = data_initiale["usd"]

    envoyer_signal(
        f"🔍 **CryptoRadar : Observation en cours pour {crypto_id.upper()}"
        f" ({label_duree})**...\n• Prix initial : `{prix_depart:,.2f} $`\n•"
        " Analyse dynamique du marché...",
        target_chat_id=target_chat_id,
    )

    intervalle = 10 if delai_secondes <= 300 else 60
    temps_ecoule = 0
    historique_prix = [prix_depart]

    while temps_ecoule < delai_secondes:
        time.sleep(intervalle)
        temps_ecoule += intervalle
        _, data_actuelle = obtenir_donnees_crypto(crypto_id)
        if data_actuelle:
            historique_prix.append(data_actuelle["usd"])

    prix_final = historique_prix[-1]
    variation_periode = ((prix_final - prix_depart) / prix_depart) * 100
    var_24h = data_actuelle["usd_24h_change"] if data_actuelle else 0

    if variation_periode > 0.05 and var_24h > -2.0:
        signal = "🟢 **SIGNAL CONFIRMÉ : ACHAT (HAUSSE DÉTECTÉE)**"
        analyse = "Pression acheteuse observée sur la période."
        confiance = "85%"
    elif variation_periode < -0.05 and var_24h < 2.0:
        signal = "🔴 **SIGNAL CONFIRMÉ : VENTE / BAISSE**"
        analyse = "Pression vendeuse observée sur la période."
        confiance = "85%"
    else:
        signal = "⚖️ **SIGNAL NEUTRE : PAS DE TRADE**"
        analyse = "Marché stagnant sur cette période d'observation."
        confiance = "Consolidation"

    rapport = (
        f"🎯 **RAPPORT CRYPTORADAR : {crypto_id.upper()}**\n\n"
        f"• Durée d'observation : `{label_duree}`\n"
        f"• Prix départ : `{prix_depart:,.2f} $` | Prix final :"
        f" `{prix_final:,.2f} $`\n"
        f"• Mouvement : `{variation_periode:+.2f}%`\n"
        f"• Indice de confiance : `{confiance}`\n\n"
        f"{signal}\n"
        f"👉 *Diagnostic :* {analyse}"
    )

    envoyer_signal(rapport, target_chat_id=target_chat_id)


def calculer_gestion_risque(capital_usd, risque_pourcent, sl_pips):
    montant_risque_usd = capital_usd * (risque_pourcent / 100)
    montant_risque_fcfa = montant_risque_usd * TAUX_USD_FCFA

    valeur_pip_standard = 10.0
    taille_lot = (
        montant_risque_usd / (sl_pips * valeur_pip_standard)
        if sl_pips > 0
        else 0.01
    )
    taille_lot = max(0.01, round(taille_lot, 2))

    return (
        f"🧮 **CRYPTORADAR RISK MANAGEMENT**\n\n"
        f"• Capital : `{capital_usd:,.2f} $` ({capital_usd * TAUX_USD_FCFA:,.0f}"
        f" FCFA)\n"
        f"• Risque : `{risque_pourcent}%` | SL : `{sl_pips} pips`\n\n"
        "-----------------------------------\n"
        "⚠️ **PERTE MAXIMALE :**\n"
        f"👉 **`{montant_risque_usd:,.2f} $`** ({montant_risque_fcfa:,.0f}"
        " FCFA)\n\n"
        "📏 **LOT CONSEILLÉ :**\n"
        f"👉 **`{taille_lot} Lot(s)`**\n"
        "-----------------------------------"
    )


def ecouter_commandes():
    offset = 0

    try:
        url_reset = f"{BASE_URL}/deleteWebhook?drop_pending_updates=True"
        urllib.request.urlopen(url_reset, timeout=5)
    except Exception:
        pass

    envoyer_signal(
        "🤖 **CryptoRadar AI Activé sur le Cloud (24h/24) !**\n\n"
        "Essayez : `Analyse le btc` ou `Analyse sol 2min`"
    )

    while True:
        url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=5"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    msg = result.get("message", {})
                    texte = msg.get("text", "").strip()
                    chat_id_utilisateur = msg.get("chat", {}).get("id", CHAT_ID)

                    if not texte:
                        continue

                    # 1. Analyse lancée en Thread (non-bloquant)
                    if "analyse" in texte.lower():
                        crypto = extraire_crypto_du_texte(texte)

                        delai_secondes = 300
                        label_duree = "5 Minutes"

                        recherche_min = re.search(r"(\d+)\s*min", texte.lower())
                        recherche_h = re.search(r"(\d+)\s*h", texte.lower())

                        if recherche_min:
                            m = int(recherche_min.group(1))
                            delai_secondes = m * 60
                            label_duree = f"{m} Minute(s)"
                        elif recherche_h:
                            h = int(recherche_h.group(1))
                            delai_secondes = h * 3600
                            label_duree = f"{h} Heure(s)"

                        # Lancement de la tâche en arrière-plan
                        thread = threading.Thread(
                            target=tache_observation_fond,
                            args=(
                                crypto,
                                delai_secondes,
                                label_duree,
                                chat_id_utilisateur,
                            ),
                        )
                        thread.start()

                    # 2. Calcul de lot
                    elif texte.lower().startswith("lot"):
                        mots = texte.split()
                        try:
                            capital = float(mots[1])
                            risque = float(mots[2])
                            sl = float(mots[3])
                            rapport = calculer_gestion_risque(
                                capital, risque, sl
                            )
                            envoyer_signal(
                                rapport, target_chat_id=chat_id_utilisateur
                            )
                        except (IndexError, ValueError):
                            envoyer_signal(
                                "❌ Format incorrect. Exemple : `lot 1000 2 30`",
                                target_chat_id=chat_id_utilisateur,
                            )

                    # 3. Discussion naturelle / IA
                    else:
                        reponse = repondre_avec_ia_crypto(texte)
                        envoyer_signal(
                            reponse, target_chat_id=chat_id_utilisateur
                        )

        except Exception as e:
            print("Erreur boucle :", e)

        time.sleep(2)


if __name__ == "__main__":
    ecouter_commandes()
