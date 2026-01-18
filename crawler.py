import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 配置区 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG Global Insights", "url": "https://www.bcg.com/rss.xml"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Financial Times", "url": "https://www.ft.com/management?format=rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Knowledge at Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss/all_articles"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
    {"name": "Wired Business", "url": "https://www.wired.com/feed/category/business/latest/rss"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/category/enterprise/feed/"}
]

BOOKS_TO_READ = ["《The Second Curve》", "《Principles》", "《High Output Management》", "《Zero to One》"]
MENTAL_MODELS = ["第一性原理 First Principles", "第二曲线 Second Curve", "飞轮效应 Flywheel Effect", "反脆弱 Antifragility", "复利效应 Compounding", "机会成本 Opportunity Cost"]

def ai_call(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60)
        content = response.json()['choices'][0]['message']['content'].strip()
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        return json.loads(content)
    except: return None

def run_sync():
    final_data = {"articles": [], "books": [], "weekly_question_en": "", "weekly_question_cn": "", "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    all_titles = []
    
    # 1. 文章抓取与中英双语联动
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for item in feed.entries[:1]:
                prompt = f"""Analyze '{item.title}'. 
                1. Match ONE model from {MENTAL_MODELS}. 
                2. Recommend ONE book from {BOOKS_TO_READ}.
                Output JSON: {{
                    "en_summary": "3 bullet points", 
                    "cn_analysis": "中文深度解析",
                    "related_model": "Model Name (中文名)", 
                    "related_book": "Book Name",
                    "scores": {{"Strategy": 80, "Org": 85, "Insight": 90, "Tech": 70, "Decision": 80}},
                    "vocabulary": {{"Word": "中文含义"}}
                }}"""
                res = ai_call(prompt)
                if res:
                    res.update({"title": item.title, "link": item.link, "source": source['name']})
                    final_data["articles"].append(res)
                    all_titles.append(item.title)
        except: continue

    # 2. 书籍笔记
    for book in BOOKS_TO_READ:
        res = ai_call(f"Deep summary for '{book}'. Output JSON: {{'book_title': '{book}', 'first_principle': '...', 'insights': ['...'], 'executive_phrasing': '...'}}")
        if res: final_data["books"].append(res)

    # 3. 生成中英双语教练提问 (Bilingual Inquiry)
    q_prompt = f"Based on news {all_titles[:5]}, generate ONE deep coaching question for a CEO. Output JSON: {{'en': 'Question in English', 'cn': '对应的中文提问'}}"
    q_res = ai_call(q_prompt)
    if q_res:
        final_data["weekly_question_en"] = q_res.get('en', "How can you leverage first principles to restructure your cost?")
        final_data["weekly_question_cn"] = q_res.get('cn', "你如何利用第一性原理重新构架你的成本结构？")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
