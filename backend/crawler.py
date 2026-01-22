import feedparser
from datetime import datetime
from typing import Dict, Optional

RSS_SOURCES = [
    {
        "name": "Harvard Business Review",
        "url": "https://hbr.org/rss/feed/topics/leadership"
    },
    {
        "name": "McKinsey Insights",
        "url": "https://www.mckinsey.com/insights/rss"
    },
    {
        "name": "The Economist - Business",
        "url": "https://www.economist.com/business/rss.xml"
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/"
    }
]


def fetch_latest_article(source: Dict) -> Optional[Dict]:
    """
    从单个 RSS 源抓取最新一篇文章
    """
    feed = feedparser.parse(source["url"])

    if not feed.entries:
        return None

    entry = feed.entries[0]

    article = {
        "source": source["name"],
        "title": entry.get("title", "").strip(),
        "summary": extract_summary(entry),
        "link": entry.get("link", ""),
        "published": extract_date(entry)
    }

    # 基础防御：标题为空直接丢弃
    if not article["title"]:
        return None

    return article


def extract_summary(entry) -> str:
    """
    尝试从 RSS 中提取摘要（有就用，没有就空）
    """
    if "summary" in entry:
        return clean_text(entry.summary)
    if "description" in entry:
        return clean_text(entry.description)
    return ""


def extract_date(entry) -> str:
    """
    提取发布时间，失败则用今天
    """
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
    except:
        pass

    return datetime.now().strftime("%Y-%m-%d")


def clean_text(text: str) -> str:
    """
    简单清洗 HTML / 多余空格
    """
    return (
        text.replace("\n", " ")
            .replace("\r", " ")
            .strip()
    )


def crawl_one() -> Optional[Dict]:
    """
    只抓一篇最有价值的内容（按 RSS 顺序）
    """
    for source in RSS_SOURCES:
        article = fetch_latest_article(source)
        if article:
            return article

    return None


if __name__ == "__main__":
    article = crawl_one()
    if article:
        print("Fetched article:")
        for k, v in article.items():
            print(f"{k}: {v}")
    else:
        print("No article fetched.")
