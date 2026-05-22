#!/usr/bin/env python3
"""Post one pending affiliate product to Telegram every run. Designed for cron."""
import psycopg2, requests, json, sys, traceback

TG_BOT_TOKEN = "8624975557:AAEDsSXNtPaUSAapozKkvbgxqpoxNbNTgWk"
TG_CHANNEL = "-1003896365741"
DB_DSN = "dbname=1ai user=postgres"

def main():
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    
    # Fetch 1 pending product
    cur.execute("""
        SELECT id, product_name, normal_price, promo_price, affiliate_link, image_url
        FROM promo_queue WHERE status = 'pending'
        ORDER BY id ASC LIMIT 1
    """)
    row = cur.fetchone()
    
    if not row:
        print("No pending products.")
        cur.close(); conn.close()
        return
    
    db_id, name, normal_price, promo_price, link, image_url = row
    n = int(normal_price)
    p = int(promo_price)
    tag = ''.join(c for c in name if c.isalnum())[:15]
    
    # Build caption
    caption = (
        f"🔥 <b>FLASH SALE MANTAP</b> 🔥\n\n"
        f"📱 <b>{name}</b>\n\n"
        f"❌ Normal: <s>Rp {n:,}</s>\n"
        f"✅ <b>Promo: Rp {p:,}</b> 😱\n\n"
        f"⏳ <i>Stok terbatas bro! Amankan di sini:</i>\n"
        f"👉 <a href=\"{link}\">Link Pembelian Promo</a>\n\n"
        f"#{tag} #FlashSale"
    )
    
    has_image = image_url and len(image_url) > 10
    
    try:
        if has_image:
            resp = requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto",
                json={
                    "chat_id": TG_CHANNEL,
                    "photo": image_url,
                    "parse_mode": "HTML",
                    "caption": caption
                },
                timeout=30
            )
            method = "sendPhoto"
        else:
            resp = requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TG_CHANNEL,
                    "text": caption,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False
                },
                timeout=30
            )
            method = "sendMessage"
        
        result = resp.json()
        
        if result.get('ok'):
            cur.execute(
                "UPDATE promo_queue SET status = 'posted', posted_at = NOW(), error_message = NULL WHERE id = %s",
                (db_id,)
            )
            conn.commit()
            print(f"✅ [{db_id}] Posted via {method}: {name[:60]}")
        else:
            error_msg = result.get('description', str(result))
            cur.execute(
                "UPDATE promo_queue SET error_message = %s WHERE id = %s",
                (f"Telegram API: {error_msg}", db_id)
            )
            conn.commit()
            print(f"❌ [{db_id}] TG error: {error_msg}")
    
    except Exception as e:
        cur.execute(
            "UPDATE promo_queue SET error_message = %s WHERE id = %s",
            (f"Exception: {str(e)[:200]}", db_id)
        )
        conn.commit()
        print(f"❌ [{db_id}] Exception: {e}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
