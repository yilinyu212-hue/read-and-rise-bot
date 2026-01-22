import feedparser
import requests

def get_full_text(url):
    """利用 Jina 抓取外刊全文，确保 Read/Rise 板块内容充实"""
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(jina_url, timeout=12)
        return response.text[:3000] # 抓取 3000 字，深度解析的黄金素材
    except: return ""

def fetch():
    # 按照 Educator 需求配置的 10 个顶级外刊源
    RSS_SOURCES = [
        {"name": "HBR-Leadership", "url": "https://hbr.org/rss/feed/topics/leadership"},
        {"name": "McKinsey-Insights", "url": "https://www.mckinsey.com/insights/rss"},
        {"name": "Economist-Business", "url": "https://www.economist.com/business/rss.xml"},
        {"name": "MIT-Sloan", "url": "https://sloanreview.mit.edu/feed/"},
        {"name": "Stanford-GSB", "url": "https://www.gsb.stanford.edu/insights/rss.xml"},
        {"name": "Knowledge-Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
        {"name": "FastCompany", "url": "https://www.fastcompany.com/latest/rss"},
        {"name": "Forbes-Strategy", "url": "https://www.forbes.com/strategy/feed/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "NYT-Business", "url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"}
    ]
    articles = []
    for src in RSS_SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            if feed.entries:
                entry = feed.entries[0]
                full_text = get_full_text(entry.link)
                articles.append({
                    "source": src["name"], "title": entry.title,
                    "content": full_text if len(full_text) > 200 else entry.get("summary", ""),
                    "url": entry.link
                })
        except: continue
    return articles
