# Telegram Affiliate Poster 🔥

Auto-post Shopee affiliate products to Telegram channel every hour.

## How It Works

```
Cron (hourly) → Pick 1 pending product → Format HTML message → Post to Telegram → Mark as posted
```

## Setup

### 1. Database
```sql
CREATE TABLE promo_queue (
    id SERIAL PRIMARY KEY,
    product_shopee_id VARCHAR(50),
    product_name TEXT NOT NULL,
    normal_price BIGINT DEFAULT 0,
    promo_price BIGINT DEFAULT 0,
    affiliate_link TEXT,
    image_url TEXT,
    product_url TEXT,
    shop_id VARCHAR(50),
    commission BIGINT DEFAULT 0,
    store_name TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    posted_at TIMESTAMP,
    error_message TEXT
);
```

### 2. Environment
```bash
# PostgreSQL (trust auth for local)
# Python dependencies
pip install psycopg2 requests
```

### 3. Cron (every 1 hour)
```bash
0 * * * * cd /path/to/repo && python3 poster.py >> /tmp/affiliate-poster.log 2>&1
```

## Configuration
Edit `poster.py`:
- `TG_BOT_TOKEN`: Telegram bot token from @BotFather
- `TG_CHANNEL`: Channel ID (e.g., `-1003896365741`)
- `DB_DSN`: PostgreSQL connection string

## Product Queue
Import products via CSV:
```sql
INSERT INTO promo_queue (product_shopee_id, product_name, normal_price, promo_price, affiliate_link, ...)
VALUES (...);
```

## Dual-mode Posting
- **Has image_url** → `sendPhoto` with HTML caption
- **No image_url** → `sendMessage` with HTML text + link

## Stats
- 100 products posted in ~4 days at 1/hour
- 58/100 products have Shopee commission
- Total potential commission: Rp 2.6M+

---
Built for BerkahKarya 🔥
