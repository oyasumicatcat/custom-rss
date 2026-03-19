import feedparser, requests, datetime
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

KEYWORDS = ["kuromi", "smart doll", "dollfie", "ドルフィー", "クロミ"]

YOUTUBE_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
]

AMiAMI_SEARCH = [
    "https://www.amiami.com/eng/c/dolls/"
]

def matches(text):
    return True
#    text = text.lower()
#    return any(k.lower() in text for k in KEYWORDS)

fg = FeedGenerator()
fg.title("ccCustom Feed")
fg.link(href="https://oyasumicatcat.github.io/custom-rss/feed.xmll")
fg.description("Auto filtered feed")

# ★ YouTube
for url in YOUTUBE_FEEDS:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        if matches(entry.title):
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.link(href=entry.link)
            fe.description(entry.summary)
            fe.pubDate(datetime.datetime.now())

# ★ AmiAmi scrape
for url in AMiAMI_SEARCH:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    for item in soup.select(".newly-added-items__item"):
        title = item.get_text(strip=True)
        link = "https://www.amiami.com" + item.find("a")["href"]

        if matches(title):
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(title)
            fe.pubDate(datetime.datetime.now())

fg.rss_file("feed.xml")
