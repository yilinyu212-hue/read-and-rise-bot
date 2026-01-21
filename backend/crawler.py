# backend/crawler.py
import feedparser
import json
import os

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"}
]

def fetch():
    articles = []
    for src in RSS_SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            if not feed.entries:
                continue
            
            # 抓取每个来源的第一条最新文章
            entry = feed.entries[0]
            articles.append({
                "source": src["name"],
                "title": entry.title,
                "content": entry.get("summary", ""),
                "url": entry.link,
                "publish_date": entry.get("published", "")
            })
        except Exception as e:
            print(f"抓取 {src['name']} 出错: {e}")

    return articles
