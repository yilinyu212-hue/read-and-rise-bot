import os, feedparser, json, requests
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
        return f"解析生成中... (API 错误: {e})"

def push_to_notion(title, link, content):
    # 【强制打印】看看机器人到底拿到了什么（安全起见只打长度）
    print(f"DEBUG: 正在尝试连接 Notion... Token 长度: {len(str(NOTION_TOKEN))}, ID 长度: {len(str(DATABASE_ID))}")
    
    try:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Source": {"select": {"name": "Economist"}}, 
                "Link": {"url": link},                       
                "AI Summary": {"rich_text": [{"text": {"content": content[:1900]}}]}, 
                "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Status": {"status": {"name": "To Read"}}
            }
        )
        print(f"🚀 终于成功了！数据已进入 Notion 看板！")
    except Exception as e:
        print(f"❌ 关键报错：Notion 服务器拒绝了请求。原因: {e}")

def run():
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    articles = []
    
    for entry in feed.entries[:3]:
        print(f"正在处理: {entry.title}")
        analysis = get_ai_analysis(entry.title)
        articles.append({"title": entry.title, "link": entry.link, "content": analysis, "date": datetime.now().strftime("%Y-%m-%d")})
        
        # 删掉了原来的 if 判断，强行尝试推送
        push_to_notion(entry.title, entry.link, analysis)

    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
