import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 强制读取配置
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def run():
    # 1. 抓取数据
    print("🚀 正在抓取经济学人...")
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    entry = feed.entries[0] # 先拿一篇文章做实验
    print(f"✅ 抓取成功: {entry.title}")

    # 2. 推送测试
    print(f"📡 正在尝试推送至 Notion... (ID: {DATABASE_ID[:5]}...)")
    try:
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Link": {"url": entry.link},
                "Status": {"status": {"name": "To Read"}}
            }
        )
        print(f"🎯 奇迹发生了！Notion 页面已创建，ID 为: {response['id']}")
    except Exception as e:
        print(f"❌ 还是失败了！Notion 服务器说: {e}")

if __name__ == "__main__":
    run()
