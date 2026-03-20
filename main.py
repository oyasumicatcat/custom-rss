import feedparser
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import time

KEYWORDS = ["kuromi", "smart doll", "dollfie", "ドルフィー", "クロミ", "doll", "pulchra", "volks", "obitsu", "azone"]

YOUTUBE_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-lHJZR3Gqxm24_Vd_AJ5Yw"
]

AMiAMI_URLS = [
    "https://www.amiami.com/eng/search/list/?s_keywords=kuromi",
]

def matches(text):
    if not text:
        return False
    text = text.lower()
    return any(k.lower() in text for k in KEYWORDS)

def fetch_with_headers(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

print("=" * 50)
print("🔍 Starting RSS Feed Generator")
print("=" * 50)

fg = FeedGenerator()
fg.title("Doll & Kuromi Feed")
fg.link(href="https://oyasumicatcat.github.io/custom-rss/feed.xml")
fg.description("Auto-updating feed for doll-related items and Kuromi merchandise")
fg.language('en')

seen_links = set()
total_entries = 0

# ★ YouTube
print("\n📺 Checking YouTube...")
for url in YOUTUBE_FEEDS:
    feed = feedparser.parse(url)
    print(f"   Found {len(feed.entries)} videos total")
    for entry in feed.entries:
        if matches(entry.title):
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.link(href=entry.link)
            fe.description(entry.get('summary', ''))
            fe.pubDate(entry.get('published', datetime.now()))
            seen_links.add(entry.link)
            total_entries += 1
            print(f"   ✅ Added: {entry.title[:50]}...")
    if len(feed.entries) == 0:
        print("   ⚠️ No videos found - channel ID might be wrong")

# ★ AmiAmi
print("\n🛍️ Checking AmiAmi...")
for url in AMiAMI_URLS:
    print(f"   Fetching: {url}")
    response = fetch_with_headers(url)
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Let's see what's on the page
        print(f"   Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Try multiple selectors that AmiAmi might use
        items = []
        possible_selectors = [".item-list", ".list-item", ".product", ".newly-added-items__item", "li.item", ".item"]
        
        for selector in possible_selectors:
            found = soup.select(selector)
            if found:
                print(f"   Found {len(found)} items with selector '{selector}'")
                items = found
                break
        
        if not items:
            print("   ❌ No items found with any selector")
            # Print first 500 chars of HTML for debugging
            print("\n   First 500 chars of HTML:")
            print(response.text[:500])
            continue
        
        for item in items[:10]:  # Limit to first 10 for debugging
            try:
                title = item.get_text(strip=True)
                link_elem = item.find("a")
                
                if link_elem:
                    link = link_elem.get("href")
                    if link and not link.startswith("http"):
                        link = "https://www.amiami.com" + link
                    
                    print(f"   Found item: {title[:50]}...")
                    
                    if matches(title) and link and link not in seen_links:
                        fe = fg.add_entry()
                        fe.title(f"[AmiAmi] {title}")
                        fe.link(href=link)
                        fe.description(f"New item found: {title}")
                        fe.pubDate(datetime.now())
                        seen_links.add(link)
                        total_entries += 1
                        print(f"   ✅ MATCHED: {title[:50]}...")
                    else:
                        if not matches(title):
                            print(f"   ⏭️ Doesn't match keywords: {title[:50]}...")
            except Exception as e:
                print(f"   ❌ Error parsing item: {e}")

print("\n" + "=" * 50)
print(f"📊 SUMMARY: Added {total_entries} total entries to feed")
print("=" * 50)

# Generate the RSS feed
fg.rss_file("feed.xml", pretty=True)
print("\n✅ Feed saved to feed.xml")
