import os, feedparser, google.generativeai as genai
from notion_client import Client

# 1. 初始化
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 关键修复：改用最基础的 'gemini-1.5-flash-latest' 或 'gemini-1.5-pro'
# 这样可以兼容大部分旧版和新版的 API 库
model = genai.GenerativeModel('gemini-1.5-flash') 

# 2. RSS 源
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
        
        # AI 简述
        prompt = f"Summarize this in Chinese (150 words) and set English level. Title: {entry.title}"
        
        try:
            response = model.generate_content(prompt)
            summary_text = response.text
        except Exception as e:
            # 如果 AI 调用还是失败，记录错误而不是让程序崩溃
            summary_text = f"AI Summary pending. Error: {str(e)}"
        
        # 3. 写入 Notion (全文字兼容模式)
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
        print(f"✅ Synced: {entry.title}")

if __name__ == "__main__":
    analyze_and_push()
