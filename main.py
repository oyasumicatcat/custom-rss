import feedparser
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import time

KEYWORDS = ["kuromi", "smart doll", "dollfie", "ドルフィー", "クロミ", "doll", "pulchra", "volks", "obitsu", "azone"]

# YouTube channels (add all your channels here)
YOUTUBE_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-lHJZR3Gqxm24_Vd_AJ5Yw",  # Your existing channel
    # Add more YouTube channels:
    # "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_2",
    # "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_3",
]

# Shopping sites
AMiAMI_URLS = [
    "https://www.amiami.com/eng/search/list/?s_keywords=kuromi",
    "https://www.amiami.com/eng/search/list/?s_keywords=dollfie",
    "https://www.amiami.com/eng/search/list/?s_keywords=smart+doll",
    "https://www.amiami.com/eng/search/list/?s_keywords=pulchra",
]

MANDARAKE_URLS = [
    "https://order.mandarake.co.jp/order/listPage/list?categoryId=13&janCode=&soldOut=0&sort=newArrival&itemKeyword=kuromi",
    "https://order.mandarake.co.jp/order/listPage/list?categoryId=13&janCode=&soldOut=0&sort=news&itemKeyword=dollfie",
]

SURUGAYA_URLS = [
    "https://www.suruga-ya.jp/search?category=&search_word=kuromi&rank_by=release_desc",
    "https://www.suruga-ya.jp/search?category=&search_word=dollfie&rank_by=release_desc",
]

# Social media (using Nitter instances for Twitter/X)
NITTER_INSTANCES = ["https://nitter.net", "https://nitter.lucabased.xyz", "https://nitter.poast.org"]
TWITTER_ACCOUNTS = [
    # Add Twitter usernames WITHOUT the @ symbol
    # "kuromi_official",
    # "dollfie_news",
]

def matches(text):
    """Check if text contains any keywords"""
    if not text:
        return False
    text = text.lower()
    return any(k.lower() in text for k in KEYWORDS)

def fetch_with_headers(url):
    """Fetch URL with browser-like headers to avoid blocking"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Initialize feed
fg = FeedGenerator()
fg.title("Doll & Kuromi Feed")
fg.link(href="https://oyasumicatcat.github.io/custom-rss/feed.xml")
fg.description("Auto-updating feed for doll-related items and Kuromi merchandise")
fg.language('en')

# Keep track of entries to avoid duplicates
seen_links = set()

# ★ YouTube
print("Fetching YouTube feeds...")
for url in YOUTUBE_FEEDS:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        if matches(entry.title) and entry.link not in seen_links:
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.link(href=entry.link)
            fe.description(entry.get('summary', ''))
            fe.pubDate(entry.get('published', datetime.now()))
            seen_links.add(entry.link)

# ★ AmiAmi
print("Fetching AmiAmi...")
for url in AMiAMI_URLS:
    response = fetch_with_headers(url)
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try different selectors that AmiAmi might use
        items = soup.select(".item-list") or soup.select(".list-item") or soup.select(".product")
        
        for item in items:
            try:
                title_elem = item.select_one(".item-name, .product-name, a")
                link_elem = item.find("a")
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get("href")
                    if not link.startswith("http"):
                        link = "https://www.amiami.com" + link
                    
                    if matches(title) and link not in seen_links:
                        fe = fg.add_entry()
                        fe.title(f"[AmiAmi] {title}")
                        fe.link(href=link)
                        fe.description(f"New item found: {title}")
                        fe.pubDate(datetime.now())
                        seen_links.add(link)
            except Exception as e:
                print(f"Error parsing AmiAmi item: {e}")

# ★ Mandarake
print("Fetching Mandarake...")
for url in MANDARAKE_URLS:
    response = fetch_with_headers(url)
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        
        for item in soup.select(".item, .product"):
            try:
                title_elem = item.select_one(".title, .name, a")
                link_elem = item.find("a")
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get("href")
                    if not link.startswith("http"):
                        link = "https://order.mandarake.co.jp" + link
                    
                    if matches(title) and link not in seen_links:
                        fe = fg.add_entry()
                        fe.title(f"[Mandarake] {title}")
                        fe.link(href=link)
                        fe.description(f"New item at Mandarake: {title}")
                        fe.pubDate(datetime.now())
                        seen_links.add(link)
            except Exception as e:
                print(f"Error parsing Mandarake item: {e}")

# ★ Suruga-ya
print("Fetching Suruga-ya...")
for url in SURUGAYA_URLS:
    response = fetch_with_headers(url)
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        
        for item in soup.select(".item, .search-result-item"):
            try:
                title_elem = item.select_one(".title, .name")
                link_elem = item.find("a")
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get("href")
                    if not link.startswith("http"):
                        link = "https://www.suruga-ya.jp" + link
                    
                    if matches(title) and link not in seen_links:
                        fe = fg.add_entry()
                        fe.title(f"[Suruga-ya] {title}")
                        fe.link(href=link)
                        fe.description(f"New item at Suruga-ya: {title}")
                        fe.pubDate(datetime.now())
                        seen_links.add(link)
            except Exception as e:
                print(f"Error parsing Suruga-ya item: {e}")

# ★ Twitter/X via Nitter (if you add accounts)
if TWITTER_ACCOUNTS:
    print("Fetching Twitter feeds...")
    for account in TWITTER_ACCOUNTS:
        for instance in NITTER_INSTANCES:
            try:
                url = f"{instance}/{account}/rss"
                feed = feedparser.parse(url)
                if feed.entries:
                    for entry in feed.entries[:10]:  # Last 10 tweets
                        if matches(entry.title) and entry.link not in seen_links:
                            fe = fg.add_entry()
                            fe.title(f"[Twitter/@{account}] {entry.title}")
                            fe.link(href=entry.link)
                            fe.description(entry.get('summary', ''))
                            fe.pubDate(entry.get('published', datetime.now()))
                            seen_links.add(entry.link)
                    break  # If one instance works, stop trying others
            except Exception as e:
                print(f"Error with {instance}/{account}: {e}")
                continue

# Generate the RSS feed
print(f"Generated {len(seen_links)} entries")
fg.rss_file("feed.xml", pretty=True)
print("Feed saved to feed.xml")
