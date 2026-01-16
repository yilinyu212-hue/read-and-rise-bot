import os, feedparser, json, google.generativeai as genai
from datetime import datetime

# 1. 配置 AI (从 GitHub Secrets 获取 Key)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 抓取外刊源 (RSS)
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
        entry = feed.entries[0] # 取每个源的最新一篇
        
        prompt = f"你是一位英语教育专家。请用中文总结这篇文章核心观点（100字以内），并提取3个核心词汇（含释义和例句）。标题: {entry.title}"
        
        try:
            # 获取 AI 真正的内容
            response = model.generate_content(prompt)
            content_text = response.text if response.text else "解析正在赶来..."
        except Exception as e:
            content_text = f"解析生成失败: {str(e)}"

        articles.append({
            "title": entry.title,
            "source": source,
            "link": entry.link,
            "content": content_text,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    # 3. 强制存入 data 文件夹
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print("✅ 数据已更新")

if __name__ == "__main__":
    analyze()
