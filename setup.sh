#!/bin/bash
# Telegram Affiliate Poster - Setup Script

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️ Creating database table..."
sudo -u postgres psql -d 1ai -c "
CREATE TABLE IF NOT EXISTS promo_queue (
    id SERIAL PRIMARY KEY,
    product_shopee_id VARCHAR(50) NOT NULL,
    product_name TEXT NOT NULL,
    normal_price BIGINT NOT NULL DEFAULT 0,
    promo_price BIGINT NOT NULL DEFAULT 0,
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
CREATE INDEX IF NOT EXISTS idx_promo_queue_status ON promo_queue(status);
CREATE INDEX IF NOT EXISTS idx_promo_queue_created ON promo_queue(created_at);
"

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit poster.py with your Telegram bot token and channel ID"
echo "2. Import products: python3 import_csv.py your_products.csv"
echo "3. Test: python3 poster.py"
echo "4. Setup cron: crontab -e"
echo "   0 * * * * cd $(pwd) && python3 poster.py >> /tmp/affiliate-poster.log 2>&1"
