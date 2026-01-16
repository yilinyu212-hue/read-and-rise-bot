import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 1. 尝试读取配置
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

def run():
    # 【核心自检】如果环境变量没读到，直接报错提醒，不继续运行
    if not NOTION_TOKEN or not DATABASE_ID:
        print("❌ 严重错误：GitHub 环境没有把 NOTION_TOKEN 或 DATABASE_ID 传给代码！")
        print("请检查你的 .yml 文件中是否写了 env: 部分。")
        return 

    notion = Client(auth=NOTION_TOKEN)
    
    print("🚀 正在抓取经济学人...")
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    if not feed.entries:
        print("❌ 抓取 RSS 失败")
        return
        
    entry = feed.entries[0]
    print(f"✅ 抓取成功: {entry.title}")

    # 推送至 Notion
    print(f"📡 正在尝试推送至 Notion... (ID: {DATABASE_ID[:4]}...)")
    try:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Link": {"url": entry.link},
                "Source": {"select": {"name": "Economist"}},
                "Status": {"status": {"name": "To Read"}}
            }
        )
        print(f"🎯 成功！请刷新 Notion 看板。")
    except Exception as e:
        print(f"❌ Notion 拒收了数据。具体原因: {e}")

if __name__ == "__main__":
    run()
