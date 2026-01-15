import os, feedparser, google.generativeai as genai
from notion_client import Client

# 1. 初始化 (Init)
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 修复核心：必须包含 models/ 前缀
model = genai.GenerativeModel('models/gemini-1.5-flash') 

# 2. RSS 源 (Sources)
RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "The Atlantic": "https://www.theatlantic.com/feed/all/",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "HBR": "https://hbr.org/rss/topic/leadership"
}

def analyze_and_push():
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        
        # AI 简述请求
        prompt = f"你是一位专业策展人。请用中文总结这篇文章的核心观点（150字以内），并标注英语难度等级(A1-C2)。标题: {entry.title}"
        
        try:
            # 尝试调用 AI
            response = model.generate_content(prompt)
            summary_text = response.text
        except Exception as e:
            # 万一 AI 还是不可用，记录错误避免程序崩溃
            summary_text = f"AI Summary pending. Error: {str(e)}"
        
        # 3. 写入 Notion
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Source": {"rich_text": [{"text": {"content": source_name}}]},
                "Link": {"url": entry.link},
                "AI Summary": {"rich_text": [{"text": {"content": summary_text}}]},
                "Status": {"rich_text": [{"text": {"content": "To Read"}}]}
            }
        )
        print(f"✅ 已同步: {entry.title}")

if __name__ == "__main__":
    analyze_and_push()
