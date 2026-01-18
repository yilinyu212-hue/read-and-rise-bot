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
MENTAL_MODELS = ["第一性原理", "第二曲线", "飞轮效应", "反脆弱", "复利效应", "机会成本", "胜任力圈"]

# ================= 2. AI 解析逻辑 =================
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
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# ================= 3. 执行同步 =================
def run_sync():
    final_data = {"articles": [], "books": [], "weekly_question": "", "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    all_titles = []
    
    print("📡 正在同步智库源并进行跨维度联动...")
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for item in feed.entries[:1]:
                prompt = f"""Analyze '{item.title}'. 
                1. Match with ONE model from {MENTAL_MODELS}. 
                2. Suggest ONE book from {BOOKS_TO_READ}.
                Output JSON: {{
                    "en_summary": "3 executive points", "cn_analysis": "### 🧠 思维模型\\n...\\n\\n### 🛠️ 决策建议\\n...",
                    "related_model": "模型名", "related_book": "关联书目",
                    "scores": {{"战略": 80, "组织": 85, "决策": 70, "视野": 90, "洞察": 80}},
                    "vocabulary": {{"Term": "Meaning"}}
                }}"""
                res = ai_call(prompt)
                if res:
                    res.update({"title": item.title, "link": item.link, "source": source['name']})
                    final_data["articles"].append(res)
                    all_titles.append(item.title)
        except: continue

    print("📚 正在生成书籍精读笔记...")
    for book in BOOKS_TO_READ:
        res = ai_call(f"Deep summary for '{book}'. Output JSON: {{'book_title': '{book}', 'first_principle': '...', 'insights': ['...'], 'executive_phrasing': '...'}}")
        if res: final_data["books"].append(res)

    print("🎙️ 正在生成教练提问...")
    q_res = ai_call(f"Based on titles {all_titles[:5]}, generate ONE deep coaching question for a CEO. JSON: {{'q': '...'}}")
    final_data["weekly_question"] = q_res.get('q', "作为领导者，你如何重构核心业务的成本结构？") if q_res else ""

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("✅ 同步完成！数据已更新。")

if __name__ == "__main__":
    run_sync()
