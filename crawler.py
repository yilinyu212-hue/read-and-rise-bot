import os, requests, json, feedparser, uuid, time
from datetime import datetime

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

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
        "messages": [
            {"role": "system", "content": "You are a Senior Executive Coach. Output strictly in JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res_j = res.json()
        if "choices" in res_j:
            return json.loads(res_j['choices'][0]['message']['content'])
    except: return None

def run():
    os.makedirs("data", exist_ok=True)
    articles = []
    
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            entry = feed.entries[0]
            
            prompt = f"""Analyze: '{entry.title}'
            As an Executive Coach, provide:
            1. Perspectives: ceo_view, org_psychology, defense_view.
            2. 3 Socratic questions for reflection.
            3. dimension_scores (Strategic, Team, Innovation, Decision, Execution) 1-10.
            4. challenge: scenario, options, correct_idx, coach_feedback.
            5. speaking_gold: A one-sentence golden quote.
            Output as JSON."""
            
            res = ask_ai(prompt)
            if res:
                res.update({"id": str(uuid.uuid4())[:6], "title": entry.title, "source": name})
                articles.append(res)
                print(f"✅ Analyzed: {name}")
        except: continue

    # 保存核心数据
    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    
    # 补全书籍和模型保底数据（防止空白）
    with open("data/books.json", "w", encoding="utf-8") as f:
        json.dump([{"title": "The Pyramid Principle", "intro": "Logical thinking for leaders."}], f)
    with open("data/models.json", "w", encoding="utf-8") as f:
        json.dump([{"name": "First Principles", "scenario": "Deep problem solving."}], f)

if __name__ == "__main__":
    run()
