import os, feedparser, json, google.generativeai as genai
from datetime import datetime

# 1. 配置 AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 抓取源
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
        
        # 增加引导语，确保 AI 返回中文
        prompt = f"请作为英语老师，用中文总结这篇文章的核心观点并列出3个重点词汇。标题: {entry.title}"
        
        try:
            response = model.generate_content(prompt)
            # 核心检查：如果 AI 返回为空，记录错误
            content_text = response.text if response.text else "AI返回内容为空，请检查Key权限"
        except Exception as e:
            content_text = f"AI生成失败，错误信息: {str(e)}"

        articles.append({
            "title": entry.title,
            "source": source,
            "link": entry.link,
            "content": content_text,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print("✅ 数据抓取完成")

if __name__ == "__main__":
    analyze()
