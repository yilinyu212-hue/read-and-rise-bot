# backend/crawler.py

import feedparser
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os


RSS_SOURCES = {
    "NYTimes": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "Economist": "https://www.economist.com/the-world-this-week/rss.xml"
}

DATA_PATH = "data/knowledge.json"


def fetch_article_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs)

        return text.strip()[:6000]  # 防止过长
    except Exception as e:
        return ""


def run_crawler(limit=3):
    results = []

    for source, rss in RSS_SOURCES.items():
        feed = feedparser.parse(rss)

        for entry in feed.entries[:limit]:
            content = fetch_article_content(entry.link)

            if len(content) < 300:
                continue

            results.append({
                "source": source,
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "content": content,
                "created_at": datetime.now().isoformat()
            })

    os.makedirs("data", exist_ok=True)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results
