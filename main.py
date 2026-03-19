import feedparser, requests, datetime
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

KEYWORDS = ["kuromi", "smart doll", "dollfie", "ドルフィー", "クロミ"]

YOUTUBE_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-lHJZR3Gqxm24_Vd_AJ5Yw"
]

AMiAMI_SEARCH = [
    "https://www.amiami.com/eng/search/list/?s_keywords=kuromi"
#    "https://rss.app/feeds/MfP0TYG2kFEph5SC.xml"
    
]

def matches(text):
    return True
    #   text = text.lower()
 #   return any(k.lower() in text for k in KEYWORDS)

fg = FeedGenerator()
fg.title("pppCustom Feed")
fg.link(href="https://oyasumicatcat.github.io/custom-rss/feed.xml")
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

# ★ AmiAmi RSS (correct way)
for url in AMiAMI_SEARCH:
    feed = feedparser.parse(url)

    for entry in feed.entries:
        if matches(entry.title):
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.link(href=entry.link)
            fe.description(entry.summary)
            fe.pubDate(datetime.datetime.now())

fg.rss_file("feed.xml")
