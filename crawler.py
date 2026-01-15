import os, feedparser, json, google.generativeai as genai
from notion_client import Client
from datetime import datetime

# 1. 初始化
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('models/gemini-1.5-flash')

# RSS 源
RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

def analyze_and_push():
    articles_for_web = []
    
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        
        # 让 AI 生成精读内容
        prompt = f"你是一位Read & Rise教育策展人。请用中文总结这篇文章核心观点（100字），标注难度(A1-C2)，并提取3个核心词汇（含释义例句）。标题: {entry.title}"
        
        try:
            response = model.generate_content(prompt)
            content = response.text
        except:
            content = "AI 解析生成中..."

        # --- 核心修复：强制截断内容，确保 Notion 不报错 ---
        safe_content = content[:1900] 

        # 尝试发送到 Notion 看板
        try:
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": entry.title[:100]}}]},
                    "Source": {"rich_text": [{"text": {"content": source_name}}]},
                    "Link": {"url": entry.link},
                    "AI Summary": {"rich_text": [{"text": {"content": safe_content}}]},
                    "Status": {"rich_text": [{"text": {"content": "Ready"}}]}
                }
            )
        except Exception as e:
            print(f"Notion 写入失败（已跳过）: {e}")
        
        # 存入列表，供网站/小程序使用
        articles_for_web.append({
            "title": entry.title,
            "source": source_name,
            "link": entry.link,
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    # 2. 确保文件夹存在并保存 JSON 数据
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles_for_web, f, ensure_ascii=False, indent=4)
    print("✅ 数据已保存到 data/library.json")

if __name__ == "__main__":
    analyze_and_push()
