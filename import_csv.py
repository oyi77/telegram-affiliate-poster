#!/usr/bin/env python3
"""Import products from CSV into promo_queue."""
import csv, sys, psycopg2

def parse_harga(s):
    s = s.strip().replace('.', '')
    if 'JT' in s:
        return int(float(s.replace('JT', '').replace(',', '.')) * 1_000_000)
    elif 'RB' in s:
        return int(float(s.replace('RB', '').replace(',', '.')) * 1_000)
    return int(s.replace(',', ''))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 import_csv.py <file.csv>")
        sys.exit(1)
    
    conn = psycopg2.connect("dbname=1ai user=postgres")
    cur = conn.cursor()
    
    with open(sys.argv[1], 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = {k.replace('\ufeff', ''): v for k, v in row.items()}
            harga = parse_harga(clean['Harga'])
            komisi_str = clean['Komisi'].replace('Rp', '').replace('.', '').strip()
            komisi = int(komisi_str) if komisi_str else 0
            
            cur.execute("""
                INSERT INTO promo_queue 
                (product_shopee_id, product_name, normal_price, promo_price, affiliate_link, product_url, shop_id, commission, store_name, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            """, (
                clean['ID Produk'],
                clean['Nama Produk'],
                harga, harga,
                clean['Link Komisi Ekstra'],
                clean['Link Produk'],
                clean['Link Produk'].split('/product/')[1].split('/')[0] if '/product/' in clean['Link Produk'] else '',
                komisi,
                clean['Nama Toko']
            ))
    
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM promo_queue")
    print(f"✅ Imported {cur.fetchone()[0]} products")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
