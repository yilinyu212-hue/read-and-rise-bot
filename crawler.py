import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 读取配置
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

# --- 外刊来源配置列表 ---
# 你可以在这里增加更多 RSS 链接，机器人会自动循环抓取
SOURCES = [
    {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
    {"name": "NYT", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"name": "The Atlantic", "url": "https://www.theatlantic.com/feed/all/"}
]

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
    print("🚀 Read & Rise 多源抓取开始...")
    all_articles = []
    
    for source in SOURCES:
        print(f"📡 正在抓取: {source['name']}...")
        feed = feedparser.parse(source['url'])
        
        # 每个来源只抓取最新的 2 篇，避免瞬间产生太多任务
        for entry in feed.entries[:2]:
            print(f"处理中: [{source['name']}] {entry.title}")
            analysis = get_ai_analysis(entry.title)
            
            # 1. 推送到 Notion
            try:
                notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": entry.title}}]},
                        "Source": {"select": {"name": source['name']}}, # 动态匹配来源名
                        "Link": {"url": entry.link},
                        "AI Summary": {"rich_text": [{"text": {"content": analysis[:1900]}}]},
                        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                        "Status": {"status": {"name": "To Read"}}
                    }
                )
                print(f"✅ Notion 同步成功")
            except Exception as e:
                print(f"❌ Notion 同步失败: {e}")

            # 2. 收集数据用于网站显示
            all_articles.append({
                "source": source['name'],
                "title": entry.title,
                "link": entry.link,
                "content": analysis,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # 3. 更新本地 library.json
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print(f"📂 本地数据已更新，共抓取 {len(all_articles)} 篇文章。")

if __name__ == "__main__":
    run()
