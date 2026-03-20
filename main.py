import feedparser, requests, datetime
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# --- Settings ---
KEYWORDS = ["kuromi", "smart doll", "dollfie", "ドルフィー", "クロミ"]

YOUTUBE_FEEDS = [
    # example format:
    # "[youtube.com](https://www.youtube.com/feeds/videos.xml?channel_id=UCXXXXXXXXXXX)",
    "[youtube.com](https://www.youtube.com/feeds/videos.xml?channel_id=UC-lHJZR3Gqxm24_Vd_AJ5Yw)",
]

CUSTOM_FEEDS = [
    # put full RSS URLs here
    # "[rss.app](https://rss.app/feeds/MfP0TYG2kFEph5SC.xml)",
    # "[nitter.net](https://nitter.net/USERNAME/rss)",
]

AMiAMI_SEARCH = [
    "[amiami.com](https://www.amiami.com/eng/search/list/?s_keywords=kuromi)",
]

# --- Filter ---
def matches(text):
    text = text.lower()
    return any(k.lower() in text for k in KEYWORDS)

# --- Setup feed ---
fg = FeedGenerator()
fg.title("Custom Kuromi Feed")
fg.link(href="[oyasumicatcat.github.io](https://oyasumicatcat.github.io/custom-rss/feed.xml)")
fg.description("Auto-updated filtered feed across sources")

# --- YouTube ---
for url in YOUTUBE_FEEDS:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        if matches(entry.title):
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.link(href=entry.link)
            fe.description(entry.get("summary", ""))
            fe.pubDate(datetime.datetime.now())

# --- Custom RSS feeds ---
for url in CUSTOM_FEEDS:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        if matches(entry.title):
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.link(href=entry.link)
            fe.description(entry.get("summary", ""))
            fe.pubDate(datetime.datetime.now())

# --- AmiAmi scrape ---
for url in AMiAMI_SEARCH:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for item in soup.select("li.item"):
        title = item.get_text(strip=True)
        link = "[amiami.com](https://www.amiami.com)" + item.find("a")["href"]
        if matches(title):
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(title)
            fe.pubDate(datetime.datetime.now())

# --- Save feed ---
fg.rss_file("feed.xml")
