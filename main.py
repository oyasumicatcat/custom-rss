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
KEYWORDS = ["kuromi", "smart doll", "dollfie", "ドルフィー", "クロミ", 
            "doll", "pulchra", "volks", "obitsu", "azone", "スーパードルフィー",
            "dollfie dream", "dd", "ドルフィードリーム"]

# ===================== SOURCE DEFINITIONS =====================
SOURCES = [
    # --- SMART DOLL (Working) ---
    {
        "name": "Smart Doll Milk",
        "url": "https://shop.smartdoll.jp/collections/filter-smart-doll-milk",
        "type": "shopify",
        "selector": ".product-item, .grid__item"
    },
    {
        "name": "Smart Doll Cinnamon",
        "url": "https://shop.smartdoll.jp/collections/filter-smart-doll-cinnamon",
        "type": "shopify",
        "selector": ".product-item, .grid__item"
    },
    
    # --- X/TWITTER VIA NITTER (Working) ---
    {
        "name": "Azone Official",
        "url": "https://nitter.net/doll_azone/rss",
        "type": "rss",
        "fallback_urls": [
            "https://nitter.poast.org/doll_azone/rss",
            "https://nitter.lucabased.xyz/doll_azone/rss"
        ]
    },
    {
        "name": "Volks Doll",
        "url": "https://nitter.net/volks_doll/rss",
        "type": "rss",
        "fallback_urls": [
            "https://nitter.poast.org/volks_doll/rss",
            "https://nitter.lucabased.xyz/volks_doll/rss"
        ]
    },
    
    # --- AMIAMI VIA FEEDER.CO (Working) ---
    {
        "name": "AmiAmi Dolls",
        "url": "https://feeder.co/discover/87ab14966d/amiami-com-eng-c-dolls",
        "type": "rss",
        "fallback_urls": []
    },
    {
        "name": "AmiAmi New Items",
        "url": "https://feeder.co/discover/c0644138e7/amiami-com-eng-c-mature-tab-1",
        "type": "rss",
        "fallback_urls": []
    },
    {
        "name": "AmiAmi Volks Search",
        "url": "https://feeder.co/discover/98c5a25d36/amiami-com-eng-search-list-s_originaltitle_id-1531",
        "type": "rss",
        "fallback_urls": []
    },
    {
        "name": "AmiAmi Licca-chan",
        "url": "https://feeder.co/discover/b59f6c870f/amiami-com-eng-search-list-s_keywords-23licca-chan-pagemax-60-s_st_list_preorder_available-1-s_st_list_backorder_available-1-s_st_list_newitem_available-1-s_st_condition_flg-1",
        "type": "rss",
        "fallback_urls": []
    },
]

# ===================== HELPER FUNCTIONS =====================
def matches(text):
    if not text:
        return False
    text = text.lower()
    # Add Japanese-to-English mappings
    text = text.replace('ドルフィー', 'dollfie').replace('スーパードルフィー', 'super dollfie')
    text = text.replace('ドルフィードリーム', 'dollfie dream')
    return any(k.lower() in text for k in KEYWORDS)

def fetch_rss_with_fallbacks(url, fallback_urls=[]):
    """Try multiple RSS URLs with detailed status"""
    all_urls = [url] + fallback_urls
    
    for i, feed_url in enumerate(all_urls):
        print(f"   Attempt {i+1}: {feed_url[:60]}...")
        try:
            feed = feedparser.parse(feed_url)
            status = getattr(feed, 'status', 'N/A')
            entries_count = len(feed.entries)
            
            print(f"      Status: {status}, Entries: {entries_count}")
            
            if entries_count > 0:
                print(f"      ✅ Success! First item: {feed.entries[0].title[:40]}...")
                return feed.entries
            
            # Check for bozo exception (parse errors)
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                print(f"      ⚠️ Parse error: {feed.bozo_exception}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"   ❌ All attempts failed for this source")
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
fg.title("Dolls & Friends Multi-Source Feed")
fg.link(href="https://oyasumicatcat.github.io/custom-rss/feed.xml")
fg.description("Combined feed from Smart Doll, Azone, Volks, and AmiAmi via Feeder")
fg.language('en')

seen_links = set()
total_entries = 0

# Process each source
for source in SOURCES:
    print(f"\n📍 Processing: {source['name']}")
    source_matches = 0
    
    if source['type'] == 'rss':
        entries = fetch_rss_with_fallbacks(
            source['url'], 
            source.get('fallback_urls', [])
        )
        
        for entry in entries[:30]:  # Limit to 30 per source
            title = entry.get('title', '')
            link = entry.get('link', '')
            if process_item(title, link, source['name']):
                source_matches += 1
                total_entries += 1
                seen_links.add(link)
                print(f"   ✅ Added: {title[:50]}...")
    
    elif source['type'] == 'shopify':
        items = fetch_shopify_page(source['url'], source['selector'])
        for item in items[:20]:
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
    fe = fg.add_entry()
    fe.title("Dolls Feed - Ready")
    fe.link(href="https://github.com/oyasumicatcat/custom-rss")
    fe.description(f"Feed configured for {len(SOURCES)} sources. Check workflow logs.")
    fe.pubDate(datetime.now(timezone.utc))
    fg.rss_file("feed.xml", pretty=True)
    print("\n⚠️ Created placeholder feed")

print("\n✅ Done!")
