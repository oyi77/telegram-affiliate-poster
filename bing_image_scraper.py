#!/usr/bin/env python3
"""Scrape product images from Bing Image Search for promo_queue products without images."""
import requests, re, time, psycopg2, urllib.parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
}

def search_bing_images(query, max_results=5):
    """Search Bing Images and return image URLs."""
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&first=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        
        # Bing stores image URLs in murl attributes (JSON-encoded)
        imgs = re.findall(r'murl&quot;:&quot;(https?://[^&]+\.(?:jpg|jpeg|png|webp)[^&]*)', r.text)
        if not imgs:
            imgs = re.findall(r'"murl":"([^"]+)"', r.text)
        
        # Filter out small/broken URLs
        valid = []
        for img in imgs:
            img = img.replace('\\/', '/')
            if len(img) < 500 and not any(x in img.lower() for x in ['icon', 'avatar', 'logo', 'favicon']):
                valid.append(img)
                if len(valid) >= max_results:
                    break
        
        return valid
    except Exception as e:
        print(f"  Bing error: {e}")
        return []

def main():
    conn = psycopg2.connect("dbname=1ai user=postgres")
    cur = conn.cursor()
    
    # Get products without images
    cur.execute("""
        SELECT id, product_name FROM promo_queue 
        WHERE image_url IS NULL 
        ORDER BY id
    """)
    products = cur.fetchall()
    print(f"Products needing images: {len(products)}")
    
    success = 0
    for db_id, name in products:
        # Clean product name for search
        search_name = name.replace('[BARU]', '').replace('[NEW]', '').replace('[', '').replace(']', '')
        # Take first 50 chars to keep query focused
        search_name = search_name[:60].strip()
        
        print(f"\n[{db_id}] Searching: {search_name[:50]}...")
        
        images = search_bing_images(search_name, max_results=3)
        
        if images:
            # Pick the best image (usually first one)
            img_url = images[0]
            cur.execute("UPDATE promo_queue SET image_url = %s WHERE id = %s", (img_url, db_id))
            conn.commit()
            success += 1
            print(f"  ✅ {img_url[:100]}")
        else:
            print(f"  ❌ No images found")
        
        # Rate limit: 2 requests per second to avoid blocking
        time.sleep(0.5)
        
        if success % 10 == 0 and success > 0:
            print(f"\n  📊 Progress: {success}/{len(products)}")
    
    conn.commit()
    cur.execute("SELECT COUNT(*) FILTER (WHERE image_url IS NOT NULL) FROM promo_queue")
    with_images = cur.fetchone()[0]
    print(f"\n✅ DONE! {success} new images | Total with images: {with_images}/{len(products)+success}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
