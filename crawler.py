import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 获取 API Key
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

# --- 10 个顶级商业/领导力源 ---
SOURCES = [
    ("HBR Leadership", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey Insights", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan Management", "https://sloanreview.mit.edu/feed/"),
    ("Strategy+Business", "https://www.strategy-business.com/rss/all_articles"),
    ("Wharton Knowledge", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Insead Knowledge", "https://knowledge.insead.edu/rss/all"),
    ("Forbes Leadership", "https://www.forbes.com/leadership/feed/"),
    ("Fast Company Strategy", "https://www.fastcompany.com/strategy/rss"),
    ("Entrepreneur Leadership", "https://www.entrepreneur.com/topic/leadership.rss"),
    ("Inc Strategy", "https://www.inc.com/rss/strategy-and-operations")
]

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are an Elite Executive Coach. Output strictly in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        data = res.json()
        if "choices" in data:
            return json.loads(data['choices'][0]['message']['content'])
    except: return None
    return None

def run():
    os.makedirs("data", exist_ok=True)
    articles = []

    print(f"--- Starting Multi-Source Sync: {len(SOURCES)} Sources ---")

    for name, url in SOURCES:
        try:
            print(f"Fetching {name}...")
            feed = feedparser.parse(requests.get(url, timeout=15).content)
            if not feed.entries: continue
            
            # 每个源只取最新的一篇，确保多样性
            entry = feed.entries[0]
            prompt = f"""
            Analyze this executive article: '{entry.title}'. 
            Output a JSON playbook for a leader:
            {{
                "title": "{entry.title}",
                "source": "{name}",
                "en_excerpt": "Select a 100-word critical paragraph from a leader's perspective",
                "cn_translation": "Professional Chinese translation",
                "vocabulary_pro": "word:contextual_meaning (list 5)",
                "insight": "AI 无法察觉的高管避坑指南 (针对中国本土落地)",
                "output_playbook": {{"speaking": "A 10-second power phrase for Monday", "writing": "Formal email template excerpt"}},
                "logic_flow": ["Step 1", "Step 2", "Step 3"]
            }}
            """
            res = ask_ai(prompt)
            if res:
                res.update({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d")})
                articles.append(res)
                print(f"✅ Success: {entry.title}")
            
            time.sleep(1) # 避免 API 频率过快
        except Exception as e:
            print(f"❌ Failed {name}: {e}")

    # 2. 确保书籍和模型也不为空
    models = [{"name": "SCQA Framework", "scenario": "High-stakes presentation", "coach_tips": "Avoid burying the lead.", "logic_flow": ["Situation", "Complication", "Question", "Answer"]}]
    books = [{"title": "The Pyramid Principle", "intro": "The gold standard for logical thinking.", "takeaways": ["Start with conclusion", "Group ideas"], "coach_tips": "Focus on the governing thought."}]

    # 保存全量数据
    with open("data/library.json", "w", encoding="utf-8") as f: json.dump(articles, f, ensure_ascii=False, indent=4)
    with open("data/models.json", "w", encoding="utf-8") as f: json.dump(models, f, ensure_ascii=False, indent=4)
    with open("data/books.json", "w", encoding="utf-8") as f: json.dump(books, f, ensure_ascii=False, indent=4)
    print(f"Sync Finished. Total Articles: {len(articles)}")

if __name__ == "__main__":
    run()
