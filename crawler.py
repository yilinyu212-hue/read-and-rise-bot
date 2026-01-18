import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 配置区 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 12 个顶级商业与科技源
RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG Global", "url": "https://www.bcg.com/rss.xml"},
    {"name": "Knowledge at Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Wired Business", "url": "https://www.wired.com/feed/category/business/latest/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Financial Times", "url": "https://www.ft.com/management?format=rss"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss/all_articles"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/category/enterprise/feed/"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
]

# 你想要 AI 精读的书籍清单
BOOKS_TO_READ = [
    "《The Second Curve》- Charles Handy",
    "《Principles》- Ray Dalio",
    "《High Output Management》- Andrew Grove",
    "《Zero to One》- Peter Thiel"
]

# ================= AI 解析核心引擎 =================
def ai_call(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60)
        content = response.json()['choices'][0]['message']['content'].strip()
        # 强制清洗 JSON 标记
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI Call Error: {e}")
        return None

def analyze_article(title, source):
    prompt = f"""You are a Business Coach. Analyze article "{title}" from {source}.
    Output JSON: {{
      "en_summary": "3 executive bullet points",
      "cn_analysis": "### 🧠 思维模型\\n...\\n\\n### 🛠️ 决策建议\\n...",
      "scores": {{"战略思维": 80, "组织进化": 80, "决策韧性": 80, "行业洞察": 80, "技术视野": 80}},
      "vocabulary": {{"Term": "Meaning"}}
    }}"""
    return ai_call(prompt)

def analyze_book(book_name):
    prompt = f"""You are a Lead Educator. Provide a deep summary for the book "{book_name}".
    Output JSON: {{
      "book_title": "{book_name}",
      "first_principle": "The core underlying logic of this book",
      "insights": ["Insight 1", "Insight 2", "Insight 3"],
      "executive_phrasing": "One classic English sentence for meetings"
    }}"""
    return ai_call(prompt)

# ================= 主运行流程 =================
def run_sync():
    final_data = {"articles": [], "books": []}
    
    # 1. 抓取外刊
    print(f"🚀 同步 12 个外刊源...")
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for item in feed.entries[:1]:
                res = analyze_article(item.title, source['name'])
                if res:
                    res.update({"title": item.title, "link": item.link, "source": source['name']})
                    final_data["articles"].append(res)
            time.sleep(1)
        except: continue

    # 2. 生成书籍精读
    print(f"📚 正在生成 AI 精读笔记...")
    for book in BOOKS_TO_READ:
        res = analyze_book(book)
        if res: final_data["books"].append(res)
        time.sleep(1)

    # 3. 持久化存储
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("✅ 全库同步完成！")

if __name__ == "__main__":
    run_sync()
