import feedparser

def fetch():
    """
    【真实抓取版】从全球顶级外刊 RSS 获取实时数据
    """
    sources = [
        {"name": "Harvard Business Review", "rss": "https://hbr.org/rss/topic/leadership", "logo": "https://hbr.org/favicon.ico"},
        {"name": "The Economist", "rss": "https://www.economist.com/business/rss.xml", "logo": "https://www.economist.com/favicon.ico"}
    ]
    
    results = []
    for s in sources:
        try:
            # 这里的代理会自动走你刚才在 FinalShell 设置的环境变量
            feed = feedparser.parse(s['rss'])
            if feed.entries:
                entry = feed.entries[0] # 取最新一篇
                results.append({
                    "source": s['name'],
                    "logo": s['logo'],
                    "title": entry.title,
                    "url": entry.link,
                    "content": entry.summary if 'summary' in entry else entry.title
                })
        except Exception as e:
            print(f"抓取 {s['name']} 失败: {e}")
            
    return results
