import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 读取配置
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

# 来源清单
SOURCES = [
    {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
    {"name": "NYT", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"name": "The Atlantic", "url": "https://www.theatlantic.com/feed/all/"}
]

def get_ai_analysis(title):
    if not DEEPSEEK_KEY: return "未配置 AI 秘钥"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
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
    except:
        return "AI 解析生成中..."

def run():
    all_articles = []
    print(f"🚀 任务开始，目标数据库: {DATABASE_ID[:5]}...")
    
    for src in SOURCES:
        print(f"📡 抓取 {src['name']}...")
        feed = feedparser.parse(src['url'])
        for entry in feed.entries[:2]: # 每个来源取2篇
            analysis = get_ai_analysis(entry.title)
            
            # 1. 同步到 Notion
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
                print(f"✅ Notion 已更新: {entry.title[:15]}")
            except Exception as e:
                print(f"❌ Notion 失败: {e}")

            # 2. 存入列表供网站使用
            all_articles.append({
                "source": src['name'],
                "title": entry.title,
                "link": entry.link,
                "content": analysis,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # 3. 彻底修复 JSON 写入，防止网站报错
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print("🎯 所有任务已完成！")

if __name__ == "__main__":
    run()
