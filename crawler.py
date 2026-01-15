import os, feedparser, google.generativeai as genai
from notion_client import Client

# 1. 初始化
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 自动寻找可用模型
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
    model = genai.GenerativeModel(model_name)
except:
    model = genai.GenerativeModel('gemini-pro')

# 2. RSS 源 (你可以根据需要继续添加)
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
        
        # --- 傻瓜式指令升级：要求 AI 生成词汇表 ---
        prompt = f"""
        你是一位专业的外刊精读老师。请针对以下文章：
        标题: {entry.title}
        
        任务：
        1. 用中文提供100字以内的核心观点总结。
        2. 标注英语难度 (A1-C2)。
        3. 挑选 3-5 个文章中的核心核心生词或短语，提供：【单词 | 音标 | 中文释义 | 原文例句】。
        
        请确保排版清晰，方便在 Notion 中阅读。
        """
        
        try:
            response = model.generate_content(prompt)
            full_content = response.text
        except Exception as e:
            full_content = f"AI暂时离线。错误详情: {str(e)}"
        
        # 3. 写入 Notion (内容全部塞进 AI Summary 这一列)
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Source": {"rich_text": [{"text": {"content": source_name}}]},
                "Link": {"url": entry.link},
                "AI Summary": {"rich_text": [{"text": {"content": full_content}}]},
                "Status": {"rich_text": [{"text": {"content": "To Read"}}]}
            }
        )
        print(f"✅ 精读包同步成功: {entry.title}")

if __name__ == "__main__":
    analyze_and_push()
