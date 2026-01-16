import os, requests, json, feedparser, uuid, time
from datetime import datetime

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

# 10 个全球顶级源
SOURCES = [
    ("HBR Leadership", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey Insights", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan", "https://sloanreview.mit.edu/feed/"),
    ("Strategy+Business", "https://www.strategy-business.com/rss/all_articles"),
    ("Wharton Knowledge", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Insead Knowledge", "https://knowledge.insead.edu/rss/all"),
    ("Forbes Leadership", "https://www.forbes.com/leadership/feed/"),
    ("Fast Company Strategy", "https://www.fastcompany.com/strategy/rss"),
    ("Entrepreneur", "https://www.entrepreneur.com/topic/leadership.rss"),
    ("Inc Strategy", "https://www.inc.com/rss/strategy-and-operations")
]

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are an Elite Executive Coach. Output strictly in JSON."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res_j = res.json()
        if "choices" in res_j:
            return json.loads(res_j['choices'][0]['message']['content'])
    except: return None
    return None

def run():
    os.makedirs("data", exist_ok=True)
    articles = []
    
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            entry = feed.entries[0]
            # 核心修改：要求 AI 生成维度分数值
            prompt = f"""Analyze the article: '{entry.title}'. 
            Output JSON: {{
                "title": "{entry.title}",
                "source": "{name}",
                "en_excerpt": "100-word paragraph",
                "cn_translation": "中文解析",
                "insight": "避坑指南",
                "dimension_scores": {{ "Strategic": 8, "Team": 7, "Innovation": 6, "Decision": 9, "Execution": 5 }},
                "output_playbook": {{ "speaking": "10-second phrase" }}
            }}"""
            res = ask_ai(prompt)
            if res:
                res.update({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%m-%d")})
                articles.append(res)
        except: continue

    # 默认书籍和模型数据
    books = [{"title": "The Pyramid Principle", "intro": "Logical thinking.", "takeaways": ["Group ideas"], "coach_tips": "Focus on clarity."}]
    models = [{"name": "SCQA Framework", "scenario": "Pitching", "coach_tips": "Build tension.", "logic_flow": ["Situation", "Complication", "Question", "Answer"]}]

    with open("data/library.json", "w", encoding="utf-8") as f: json.dump(articles, f, ensure_ascii=False, indent=4)
    with open("data/books.json", "w", encoding="utf-8") as f: json.dump(books, f, ensure_ascii=False, indent=4)
    with open("data/models.json", "w", encoding="utf-8") as f: json.dump(models, f, ensure_ascii=False, indent=4)
    print("Sync complete.")

if __name__ == "__main__":
    run()
