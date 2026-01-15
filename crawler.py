import os, feedparser, json, google.generativeai as genai
from notion_client import Client
from datetime import datetime

# 1. 初始化
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 模型选择
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
    model = genai.GenerativeModel(model_name)
except:
    model = genai.GenerativeModel('gemini-pro')

RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "The Atlantic": "https://www.theatlantic.com/feed/all/",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

def analyze_and_push():
    articles_for_web = []
    
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        
        # 让 AI 生成适合精读网站的格式
        prompt = f"你是一位Read & Rise教育策展人。请用中文总结这篇文章核心观点（100字），标注难度等级(A1-C2)，并提取3个重点单词（含释义和原句）。标题: {entry.title}"
        
        try:
            response = model.generate_content(prompt)
            content = response.text
        except:
            content = "内容生成中..."

        # 同步 Notion 看板
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Source": {"rich_text": [{"text": {"content": source_name}}]},
                "Link": {"url": entry.link},
                "AI Summary": {"rich_text": [{"text": {"content": content}}]},
                "Status": {"rich_text": [{"text": {"content": "Ready"}}]}
            }
        )
        
        # 存入列表准备写成 JSON
        articles_for_web.append({
            "title": entry.title,
            "source": source_name,
            "link": entry.link,
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    # 保存文件给网站/小程序用
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles_for_web, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    analyze_and_push()
