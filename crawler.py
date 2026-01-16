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
        # 这里严格对齐你的 Notion 截图列名
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Source": {"select": {"name": "Economist"}}, # 对应你的彩色 Source 标签
                "Link": {"url": link},                       # 对应你的 Link 图标列
                "AI Summary": {"rich_text": [{"text": {"content": content[:1900]}}]}, # 对应摘要
                "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Status": {"status": {"name": "To Read"}}    # 对应你的 Status 状态列
            }
        )
        print(f"✅ 成功同步一篇文章到 Notion: {title}")
    except Exception as e:
        print(f"❌ Notion推送单条失败: {e}")

def run():
    # 爬取经济学人数据
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    articles = []
    
    for entry in feed.entries[:3]:
        print(f"正在处理文章: {entry.title}")
        analysis = get_ai_analysis(entry.title)
        
        # 1. 准备本地 JSON 数据
        articles.append({
            "title": entry.title, 
            "link": entry.link, 
            "content": analysis, 
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        
        # 2. 推送到 Notion
        if NOTION_TOKEN and DATABASE_ID:
            push_to_notion(entry.title, entry.link, analysis)

    # 3. 保存到本地文件供网站读取
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
