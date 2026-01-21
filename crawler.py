import feedparser, json, os
from datetime import datetime

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"}
]

OUTPUT_FILE = "data/articles_raw.json"

def fetch():
    articles = []
    for src in RSS_SOURCES:
        feed = feedparser.parse(src["url"])
        if not feed.entries:
            continue

        entry = feed.entries[0]
        articles.append({
            "id": f"{src['name']}_{entry.published}",
            "title": entry.title,
            "content": entry.get("summary", ""),
            "source": src["name"],
            "url": entry.link,
            "publish_date": entry.get("published", "")
        })

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Fetched {len(articles)} articles.")

if __name__ == "__main__":
    fetch()
