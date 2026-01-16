import os, feedparser, json, google.generativeai as genai
from datetime import datetime

# 1. 配置 AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 抓取源
RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "The Atlantic": "https://www.theatlantic.com/feed/all/",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

def analyze():
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        
        # 尝试让 AI 生成，如果失败则用原文摘要保底
        prompt = f"请简要总结这篇文章核心观点。标题: {entry.title}"
        try:
            response = model.generate_content(prompt)
            # 如果 AI 返回了内容就用 AI 的，否则用原文摘要
            content_text = response.text if (response and response.text) else entry.get('summary', '点击链接查看原文')
        except:
            content_text = entry.get('summary', '精选外刊深度阅读，欢迎点击链接查看详情。')[:200]

        articles.append({
            "title": entry.title,
            "source": source,
            "link": entry.link,
            "content": content_text,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    # 3. 写入文件
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print("✅ 数据已强制写入 library.json")

if __name__ == "__main__":
    analyze()
