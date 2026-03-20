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
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.description(entry.summary)
            
# ★ AmiAmi scrape
for url in AMiAMI_SEARCH:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    for item in soup.select("li.item"):
        title = item.get_text(strip=True)
        link = "https://www.amiami.com" + item.find("a")["href"]

        fe = fg.add_entry()
        fe.title(title)
        fe.link(href=link)
        fe.description(title)
        
fg.rss_file("feed.xml")
