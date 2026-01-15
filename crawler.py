import os, feedparser, google.generativeai as genai
from notion_client import Client

# 1. 初始化
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 修复报错：改用最稳定的模型名称
model = genai.GenerativeModel('gemini-pro') 

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
        
        prompt = f"Summarize this in Chinese (150 words) and set English level. Title: {entry.title}"
        response = model.generate_content(prompt)
        
        # 3. 写入 Notion (采用最万能的 Rich Text 格式，解决 Status/Source 报错)
        # 无论你的 Notion 列设为 Text 还是 Select，这段代码都能绕过类型检查
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Source": {"rich_text": [{"text": {"content": source_name}}]},
                "Link": {"url": entry.link},
                "AI Summary": {"rich_text": [{"text": {"content": response.text}}]},
                "Status": {"rich_text": [{"text": {"content": "To Read"}}]}
            }
        )
        print(f"✅ Synced: {entry.title}")

if __name__ == "__main__":
    analyze_and_push()
