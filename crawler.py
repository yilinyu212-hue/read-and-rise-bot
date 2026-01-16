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
        return "解析生成中..."

def push_to_notion(title, link, content):
    try:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Source": {"select": {"name": "Economist"}}, # 匹配你的 Source 选项
                "Link": {"url": link},                       # 匹配你的 Link 列
                "AI Summary": {"rich_text": [{"text": {"content": content[:1900]}}]}, # 匹配 AI Summary
                "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            }
        )
    except Exception as e:
        print(f"Notion推送失败: {e}")

def run():
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    articles = []
    
    for entry in feed.entries[:3]:
        analysis = get_ai_analysis(entry.title)
        # 存入本地文件
        articles.append({"title": entry.title, "link": entry.link, "content": analysis, "date": datetime.now().strftime("%Y-%m-%d")})
        # 同步推送到 Notion
        if NOTION_TOKEN and DATABASE_ID:
            push_to_notion(entry.title, entry.link, analysis)

    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
