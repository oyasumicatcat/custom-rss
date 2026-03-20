import feedparser
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import time
import random

print("🚀 Starting Multi-Source Dolls Feed")
print("=" * 50)

# ===================== CONFIGURATION =====================
# Your keywords for filtering
KEYWORDS = ["kuromi", "smart doll", "dollfie", "ドルフィー", "クロミ", 
            "doll", "pulchra", "volks", "obitsu", "azone", "スーパードルフィー"]

# ===================== SOURCE DEFINITIONS =====================
SOURCES = [
    # --- EASY: Smart Doll Shop (Product Pages) ---
    {
        "name": "Smart Doll Milk",
        "url": "https://shop.smartdoll.jp/collections/filter-smart-doll-milk",
        "type": "shopify",  # They use Shopify
        "selector": ".product-item, .grid__item"
    },
    {
        "name": "Smart Doll Cinnamon",
        "url": "https://shop.smartdoll.jp/collections/filter-smart-doll-cinnamon",
        "type": "shopify",
        "selector": ".product-item, .grid__item"
    },
    
    # --- MEDIUM: AmiAmi (Try RSS First) ---
    {
        "name": "AmiAmi Dolls RSS",
        "url": "https://www.amiami.com/feeds/c/dolls/",
        "type": "rss"
    },
    {
        "name": "AmiAmi Volks Search RSS",
        "url": "https://www.amiami.com/feeds/search/?s_originaltitle_id=1531",
        "type": "rss"
    },
    
    # --- HARD: X/Twitter via Nitter ---
    {
        "name": "Azone Official (X)",
        "url": "https://nitter.net/doll_azone/rss",
        "type": "rss",
        "fallback_url": "https://nitter.poast.org/doll_azone/rss"  # Backup instance
    },
    {
        "name": "Volks Doll (X)",
        "url": "https://nitter.net/volks_doll/rss",
        "type": "rss",
        "fallback_url": "https://nitter.lucabased.xyz/volks_doll/rss"
    },
    
    # --- VERY HARD: Mandarake (Needs Special Handling) ---
    {
        "name": "Mandarake Dollfie Dream",
        "url": "https://order.mandarake.co.jp/order/listPage/list?categoryCode=020114&keyword=%e3%83%89%e3%83%ab%e3%83%95%e3%82%a3%e3%83%bc%e3%83%89%e3%83%aa%e3%83%bc%e3%83%a0",
        "type": "mandarake",
        "enabled": False  # Start with this disabled until we solve it
    },
]

# ===================== HELPER FUNCTIONS =====================
def matches(text):
    if not text:
        return False
    text = text.lower()
    # Add Japanese-to-English mappings
    text = text.replace('ドルフィー', 'dollfie').replace('スーパードルフィー', 'super dollfie')
    return any(k.lower() in text for k in KEYWORDS)

def fetch_rss(url):
    """Fetch and parse an RSS feed"""
    try:
        feed = feedparser.parse(url)
        print(f"   Status: {getattr(feed, 'status', 'N/A')}")
        print(f"   Entries: {len(feed.entries)}")
        return feed.entries
    except Exception as e:
        print(f"   ❌ RSS Error: {e}")
        return []

def fetch_shopify_page(url, selector):
    """Scrape a Shopify product page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select(selector)
            print(f"   Found {len(items)} potential items")
            return items
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return []

def process_item(title, link, source_name):
    """Add item to feed if it matches keywords"""
    if title and link and matches(title):
        fe = fg.add_entry()
        fe.title(f"[{source_name}] {title[:100]}")
        fe.link(href=link)
        fe.description(f"Found at {source_name}")
        fe.pubDate(datetime.now(timezone.utc))
        return True
    return False

# ===================== MAIN FEED GENERATION =====================
fg = FeedGenerator()
fg.title("Multi-Source Dolls Feed")
fg.link(href="https://oyasumicatcat.github.io/custom-rss/feed.xml")
fg.description("Combined feed from multiple doll sources")
fg.language('en')

seen_links = set()
total_entries = 0

# Process each source
for source in SOURCES:
    if not source.get('enabled', True):
        print(f"\n⏭️ Skipping {source['name']} (disabled)")
        continue
    
    print(f"\n📍 Processing: {source['name']}")
    source_matches = 0
    
    if source['type'] == 'rss':
        # Try main URL, then fallback
        entries = fetch_rss(source['url'])
        if not entries and 'fallback_url' in source:
            print(f"   Trying fallback: {source['fallback_url']}")
            entries = fetch_rss(source['fallback_url'])
        
        for entry in entries[:20]:
            title = entry.get('title', '')
            link = entry.get('link', '')
            if process_item(title, link, source['name']):
                source_matches += 1
                total_entries += 1
                seen_links.add(link)
                print(f"   ✅ Added: {title[:50]}...")
    
    elif source['type'] == 'shopify':
        items = fetch_shopify_page(source['url'], source['selector'])
        for item in items[:15]:
            try:
                # Find title and link
                link_elem = item.find('a')
                title = item.get_text(strip=True)
                if link_elem:
                    link = link_elem.get('href')
                    if link and not link.startswith('http'):
                        link = "https://shop.smartdoll.jp" + link
                    
                    if process_item(title, link, source['name']):
                        source_matches += 1
                        total_entries += 1
                        seen_links.add(link)
                        print(f"   ✅ Added: {title[:50]}...")
            except:
                continue
    
    print(f"   📊 Matches: {source_matches}")

print("\n" + "=" * 50)
print(f"📊 TOTAL: Added {total_entries} entries")
print("=" * 50)

# Generate feed
if total_entries > 0:
    fg.rss_file("feed.xml", pretty=True)
    print(f"\n✅ Feed saved with {total_entries} entries")
else:
    # Create a test entry
    fe = fg.add_entry()
    fe.title("Dolls Feed - Ready")
    fe.link(href="https://github.com/oyasumicatcat/custom-rss")
    fe.description(f"Feed configured for {len(SOURCES)} sources. Check workflow logs.")
    fe.pubDate(datetime.now(timezone.utc))
    fg.rss_file("feed.xml", pretty=True)
    print("\n⚠️ Created placeholder feed")

print("\n✅ Done!")
