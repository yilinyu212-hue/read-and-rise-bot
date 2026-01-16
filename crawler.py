import os, feedparser, json, google.generativeai as genai
from datetime import datetime

# 1. 配置 AI
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = None

# 2. 定义抓取源
RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

def analyze():
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        
        # 默认使用原文摘要作为保底内容
        content_text = entry.get('summary', '点击链接阅读外刊深度原文。')[:300]
        
        # 尝试让 AI 总结（如果 AI 成功，会覆盖掉上面的保底内容）
        if model:
            try:
                response = model.generate_content(f"请用中文总结这篇文章核心观点：{entry.title}")
                if response and response.text:
                    content_text = response.text
            except:
                pass 

        articles.append({
            "title": entry.title,
            "source": source,
            "link": entry.link,
            "content": content_text, # 即使 AI 失败，这里现在也有文章摘要了
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    # 3. 写入文件
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    analyze()
