import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 配置 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "Knowledge@Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"}
]

BOOKS_TO_READ = [
    "《The Second Curve》- Charles Handy",
    "《Principles》- Ray Dalio",
    "《High Output Management》- Andrew Grove",
    "《Zero to One》- Peter Thiel"
]

# 预设的 10 个思维模型，供 AI 匹配
MENTAL_MODELS = [
    "第一性原理", "第二曲线", "飞轮效应", "边际安全", "帕累托法则",
    "复利效应", "机会成本", "反脆弱", "胜任力圈", "均值回归"
]

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
    except: return None

def analyze_article(title, source):
    # 核心：要求 AI 进行联动匹配
    prompt = f"""
    Analyze article '{title}' from {source}. 
    1. Match it with ONE model from: {MENTAL_MODELS}.
    2. Recommend ONE book from: {BOOKS_TO_READ}.
    Output JSON: {{
      "en_summary": "3 executive bullet points",
      "cn_analysis": "### 🧠 思维模型\\n...\\n\\n### 🛠️ 决策建议\\n...",
      "related_model": "Selected Model Name",
      "recommended_book": "Selected Book Name",
      "scores": {{"战略": 80, "组织": 85, "决策": 70, "视野": 90, "技术": 75}},
      "vocabulary": {{"Term": "Meaning"}}
    }}
    """
    return ai_call(prompt)

def analyze_book(book_name):
    prompt = f"Summary for '{book_name}'. JSON: {{'book_title': '{book_name}', 'first_principle': '...', 'insights': ['...', '...', '...'], 'executive_phrasing': '...'}}"
    return ai_call(prompt)

# ================= 3. 同步流程 =================
def run_sync():
    final_data = {"articles": [], "books": [], "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    print("📡 同步智库源...")
    for source in RSS_SOURCES:
        feed = feedparser.parse(source['url'])
        for item in feed.entries[:1]:
            res = analyze_article(item.title, source['name'])
            if res:
                res.update({"title": item.title, "link": item.link, "source": source['name']})
                final_data["articles"].append(res)
        time.sleep(1)

    print("📚 生成精读笔记...")
    for book in BOOKS_TO_READ:
        res = analyze_book(book)
        if res: final_data["books"].append(res)
        time.sleep(1)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("✅ 全库联动更新完成")

if __name__ == "__main__":
    run_sync()
