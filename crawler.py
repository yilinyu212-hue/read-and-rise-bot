import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 配置从 GitHub Secrets 中读取
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

# 增加外刊来源列表
SOURCES = [
    {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
    {"name": "NYT", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"name": "The Atlantic", "url": "https://www.theatlantic.com/feed/all/"}
]

def get_ai_analysis(title):
    if not DEEPSEEK_KEY: return "AI 密钥未配置"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位教育策展人。请用中文总结核心观点、标注难度并提取3个重点词汇。"},
            {"role": "user", "content": f"文章标题: {title}"}
        ]
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except:
        return "AI 正在解析中..."

def run():
    all_articles = []
    print(f"🚀 开始同步多源外刊到 Notion (ID: {DATABASE_ID[:5]}...)")
    
    for src in SOURCES:
        print(f"📡 抓取 {src['name']}...")
        feed = feedparser.parse(src['url'])
        
        # 每个来源同步最新的 2 篇
        for entry in feed.entries[:2]:
            analysis = get_ai_analysis(entry.title)
            
            # 1. 同步到 Notion (确保字段名 Name, Source, Link, AI Summary, Date, Status 正确)
            try:
                notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": entry.title}}]},
                        "Source": {"select": {"name": src['name']}},
                        "Link": {"url": entry.link},
                        "AI Summary": {"rich_text": [{"text": {"content": analysis[:1900]}}]},
                        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                        "Status": {"status": {"name": "To Read"}}
                    }
                )
                print(f"✅ Notion 已接收: {entry.title[:15]}...")
            except Exception as e:
                print(f"❌ Notion 同步失败: {e}")

            # 2. 收集数据用于精读网站
            all_articles.append({
                "source": src['name'],
                "title": entry.title,
                "link": entry.link,
                "content": analysis,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # 3. 彻底修复 library.json 写入格式
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print("🎯 同步圆满完成！")

if __name__ == "__main__":
    run()
