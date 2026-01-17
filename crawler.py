import os
import requests
import feedparser # 需要执行 pip install feedparser
from datetime import datetime

# --- 配置区 ---
DEEPSEEK_KEY = "sk-500a770ac8e74c4cb38286ba27164c4a"
NOTION_TOKEN = "ntn_6058092242690eiABGM9YMvb0HPUXg9K40aFAfe1H59CV"
DATABASE_ID = "2e9e1ae7843a80ce8fe1f187a5adda68"

# 你提供的 10 个外刊源 (RSS 地址)
SOURCES = {
    "The Economist": "https://www.economist.com/finance-and-economics/rss.xml",
    "Harvard Business Review": "https://hbr.org/rss/topic/leadership",
    "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/Education.xml",
    "MIT Sloan Management": "https://sloanreview.mit.edu/feed/",
    "McKinsey Insights": "https://www.mckinsey.com/insights/rss",
    "Fast Company": "https://www.fastcompany.com/leadership/rss",
    "Forbes Leadership": "https://www.forbes.com/leadership/feed/",
    "Wired": "https://www.wired.com/feed/category/business/latest/rss",
    "Nature (Science)": "https://www.nature.com/nature.rss",
    "Stanford News": "https://news.stanford.edu/feed/"
}

def fetch_rss_articles():
    """扫描所有源，抓取最新文章标题"""
    new_articles = []
    for source_name, url in SOURCES.items():
        print(f"📡 正在扫描 {source_name}...")
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # 每个源只取最新的3篇
            new_articles.append({
                "title": entry.title,
                "link": entry.link,
                "source": source_name
            })
    return new_articles

def create_notion_task(title, source, link):
    """把抓取到的文章存入 Notion 待处理队列"""
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Category": {"select": {"name": "📰 Foreign Publication"}},
            "Status": {"select": {"name": "Pending"}},
            "Source_Link": {"url": link}
        }
    }
    requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)

def run_auto_pipeline():
    # 1. 抓取文章
    articles = fetch_rss_articles()
    
    # 2. 存入 Notion (这里可以加个查重逻辑，避免重复抓取)
    for art in articles:
        print(f"📝 正在同步到 Notion: {art['title']}")
        create_notion_task(art['title'], art['source'], art['link'])
    
    # 3. 接下来你可以运行之前的 AI 解析逻辑，把这些 Pending 的文章变成功课
    print("🚀 抓取完成！现在你可以运行 AI 解析器了。")

if __name__ == "__main__":
    run_auto_pipeline()
