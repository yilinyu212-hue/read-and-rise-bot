import feedparser
import requests

def get_full_text(url):
    """【核心升级】利用 Jina 抓取外刊全文，确保 Read/Rise 板块有真实案例支撑"""
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(jina_url, timeout=12)
        # 抓取 3000 字，让 AI 有充足素材生成中英文解析
        return response.text[:3000] 
    except: return ""

def fetch():
    # 按照合伙人要求配置的 10 个顶级外刊源
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
