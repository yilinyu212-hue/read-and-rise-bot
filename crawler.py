import os, feedparser, google.generativeai as genai
from notion_client import Client

# 1. 初始化
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 自动寻找可用模型 (解决 404 的终极方案)
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # 优先选择 1.5-flash，没有就选第一个可用的
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
    model = genai.GenerativeModel(model_name)
except Exception:
    model = genai.GenerativeModel('gemini-pro')

# 2. RSS 源
RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "The Atlantic": "https://www.theatlantic.com/feed/all/",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

def analyze_and_push():
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        
        # 优化提示词
        prompt = f"你是Read & Rise的策展人。请用中文总结这篇文章核心观点（100字），并标注英语难度(A1-C2)。标题: {entry.title}"
        
        try:
            response = model.generate_content(prompt)
            summary_text = response.text
        except Exception as e:
            summary_text = f"AI暂时离线，请检查API状态。错误详情: {str(e)}"
        
        # 3. 写入 Notion
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Source": {"rich_text": [{"text": {"content": source_name}}]},
                "Link": {"url": entry.link},
                "AI Summary": {"rich_text": [{"text": {"content": summary_text}}]},
                "Status": {"rich_text": [{"text": {"content": "To Read"}}]}
            }
        )
        print(f"✅ 同步成功: {entry.title}")

if __name__ == "__main__":
    analyze_and_push()
