import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 读取配置
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_ai_analysis(title):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位Read & Rise教育策展人。请用中文总结核心观点、标注难度并提取3个重点词汇。"},
            {"role": "user", "content": f"文章标题: {title}"}
        ]
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI解析生成中... (错误: {e})"

def run():
    print("🚀 正在抓取并同步...")
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    articles = []
    
    # 每次同步最新的 3 篇
    for entry in feed.entries[:3]:
        print(f"处理中: {entry.title}")
        analysis = get_ai_analysis(entry.title)
        
        # 1. 推送到 Notion
        try:
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": entry.title}}]},
                    "Source": {"select": {"name": "Economist"}},
                    "Link": {"url": entry.link},
                    "AI Summary": {"rich_text": [{"text": {"content": analysis[:1900]}}]},
                    "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                    "Status": {"status": {"name": "To Read"}}
                }
            )
            print(f"✅ Notion 已更新: {entry.title[:15]}")
        except Exception as e:
            print(f"❌ Notion 推送失败: {e}")

        # 2. 收集数据用于网站显示
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "content": analysis,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    # 3. 保存 library.json 供精读网站读取
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print("📂 library.json 已更新，精读网站数据就绪。")

if __name__ == "__main__":
    run()
