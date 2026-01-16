import os, feedparser, json, requests
from datetime import datetime
from notion_client import Client

# 从 GitHub Secrets 中读取配置
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
        return f"AI解析生成中... (错误详情: {e})"

def push_to_notion(title, link, content):
    try:
        # 调试信息：打印 ID 长度确保 Secret 已生效
        print(f"DEBUG: 尝试推送至 Database ID (长度: {len(DATABASE_ID)})")
        
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Source": {"select": {"name": "Economist"}}, 
                "Link": {"url": link},                       
                "AI Summary": {"rich_text": [{"text": {"content": content[:1900]}}]}, 
                "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Status": {"status": {"name": "To Read"}}  # 匹配你看板中的 'To Read' 状态
            }
        )
        print(f"🚀 成功同步一篇文章到 Notion: {title[:20]}...")
    except Exception as e:
        print(f"❌ Notion 推送失败。错误原因: {e}")

def run():
    # 爬取经济学人 Briefing 栏目
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    articles = []
    
    # 每次处理前 3 篇
    for entry in feed.entries[:3]:
        print(f"正在处理: {entry.title}")
        analysis = get_ai_analysis(entry.title)
        
        articles.append({
            "title": entry.title, 
            "link": entry.link, 
            "content": analysis, 
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        
        if NOTION_TOKEN and DATABASE_ID:
            push_to_notion(entry.title, entry.link, analysis)

    # 保存本地 library.json
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
