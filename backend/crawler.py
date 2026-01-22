import feedparser
import requests
from bs4 import BeautifulSoup


def fetch_article(url: str) -> str:
    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text() for p in paragraphs)

    return text


def fetch_from_rss(rss_url: str):
    feed = feedparser.parse(rss_url)
    entry = feed.entries[0]

    title = entry.title
    link = entry.link
    content = fetch_article(link)

    return title, content
