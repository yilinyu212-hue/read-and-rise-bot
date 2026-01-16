import os, feedparser, json, requests
from datetime import datetime
from notion_client import Client

# 1. 配置钥匙
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
    except:
        return "AI解析生成中..."

def push_to_notion(title, link, content):
    try:
        # 这里严格对应你看板的 6 个列名
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Source": {"select": {"name": "Economist"}}, 
                "Link": {"url": link},                       
                "AI Summary": {"rich_text": [{"text": {"content": content[:1900]}}]}, 
                "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Status": {"status": {"name": "To Read"}}  # 必须和看板里的状态名一致
            }
        )
        print(f"✅ 成功：'{title[:15]}...' 已送达 Notion")
    except Exception as e:
        print(f"❌ 失败：无法存入 Notion。错误详情: {e}")

def run():
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    articles = []
    
    for entry in feed.entries[:3]:
        print(f"正在抓取: {entry.title}")
        analysis = get_ai_analysis(entry.title)
        
        # 存入本地 JSON (供网站读取)
        articles.append({"title": entry.title, "link": entry.link, "content": analysis, "date": datetime.now().strftime("%Y-%m-%d")})
        
        # 同步到 Notion
        if NOTION_TOKEN and DATABASE_ID:
            push_to_notion(entry.title, entry.link, analysis)

    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
