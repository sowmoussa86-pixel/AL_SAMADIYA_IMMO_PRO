import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID") # ex: @alsamadiyaimmo

FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_IDS = os.getenv("FB_PAGE_IDS", "").split(",") # ids de tes pages: IMMO,MARKET,sentotv

def publier_annonce_auto(annonce, image_url=None):
    titre = annonce.titre
    prix = f"{annonce.prix:,.0f} FCFA"
    lien = f"https://al-samadiya-immo-pro.onrender.com/annonce/{annonce.id}"
    
    texte = f"""🏠 {titre}
💰 {prix} | 📍 {annonce.ville} - {annonce.quartier}
{annonce.description[:150]}...

👉 Voir + photos & contacter : {lien}

#ImmobilierSenegal #Dakar #AlSamadiyaImmo #Terrain #Maison"""

    # 1. TELEGRAM (le plus facile, 2 min)
    if TELEGRAM_BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": texte, "photo": image_url} if image_url else {"chat_id": TELEGRAM_CHANNEL_ID, "text": texte}
            requests.post(url, data=data, timeout=10)
            print("✅ Telegram publié")
        except Exception as e:
            print(f"Telegram error {e}")

    # 2. FACEBOOK (multi-pages)
    for page_id in FB_PAGE_IDS:
        try:
            if image_url:
                requests.post(f"https://graph.facebook.com/{page_id}/photos", data={"url": image_url, "message": texte, "access_token": FB_PAGE_TOKEN}, timeout=15)
            else:
                requests.post(f"https://graph.facebook.com/{page_id}/feed", data={"message": texte, "link": lien, "access_token": FB_PAGE_TOKEN}, timeout=15)
            print(f"✅ Facebook {page_id} publié")
        except Exception as e:
            print(f"FB {page_id} error {e}")

    # Pour Instagram / LinkedIn / TikTok on ajoute après avec tes tokens
