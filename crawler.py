import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 环境配置 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 12 个顶级商业源
RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG Global", "url": "https://www.bcg.com/rss.xml"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
    # ... 其他源可继续添加 ...
]

# AI 精读书籍清单
BOOKS_TO_READ = [
    "《The Second Curve》- Charles Handy",
    "《Principles》- Ray Dalio",
    "《High Output Management》- Andrew Grove"
]

MENTAL_MODELS = ["第一性原理", "第二曲线", "飞轮效应", "反脆弱", "复利效应"]

# ================= 2. AI 解析引擎 =================
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

def analyze_article(title, source):
    prompt = f"""Analyze '{title}' from {source}. 
    Match with ONE model from {MENTAL_MODELS}.
    Output JSON: {{
      "en_summary": "3 executive points",
      "cn_analysis": "### 🧠 思维模型\\n...\\n\\n### 🛠️ 决策建议\\n...",
      "related_model": "Model Name",
      "scores": {{"战略": 85, "组织": 80, "视野": 90, "进化": 85, "洞察": 88}},
      "vocabulary": {{"Term": "Meaning"}}
    }}"""
    return ai_call(prompt)

def analyze_book(book_name):
    prompt = f"Deep summary for '{book_name}'. JSON: {{'book_title': '{book_name}', 'first_principle': '...', 'insights': ['...', '...'], 'executive_phrasing': '...'}}"
    return ai_call(prompt)

# ================= 3. 主流程 =================
def run_sync():
    final_data = {"articles": [], "books": [], "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    for source in RSS_SOURCES:
        feed = feedparser.parse(source['url'])
        for item in feed.entries[:1]:
            res = analyze_article(item.title, source['name'])
            if res:
                res.update({"title": item.title, "link": item.link, "source": source['name']})
                final_data["articles"].append(res)
    
    for book in BOOKS_TO_READ:
        res = analyze_book(book)
        if res: final_data["books"].append(res)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
