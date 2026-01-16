import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 获取 API Key
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

# 10 个全球顶级商业/领导力源
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
        "messages": [{"role": "system", "content": "You are an Elite Executive Coach. Output strictly in valid JSON."}, {"role": "user", "content": prompt}],
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
    
    # 1. 处理 10 个外刊源
    articles = []
    print("--- Starting Multi-Source Sync ---")
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            entry = feed.entries[0]
            prompt = f"Analyze: '{entry.title}'. JSON: {{'title':'{entry.title}','source':'{name}','en_excerpt':'Critical paragraph','cn_translation':'中文解析','insight':'避坑指南','output_playbook':{{'speaking':'Monday phrase'}}}}"
            res = ask_ai(prompt)
            if res:
                res.update({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%m-%d")})
                articles.append(res)
                print(f"✅ Synced: {name}")
            time.sleep(1)
        except: continue

    # 2. 深度书架 (模拟生成)
    books = []
    for b_name in ["The Pyramid Principle", "Atomic Habits"]:
        b_res = ask_ai(f"Summarize book '{b_name}'. JSON: {{'title':'{b_name}','intro':'简介','takeaways':['A','B'],'coach_tips':'阅读建议'}}")
        if b_res: books.append(b_res)

    # 3. 思维模型
    models = [{"name": "SCQA Framework", "scenario": "High-stakes presentation", "coach_tips": "Start with context.", "logic_flow": ["Situation", "Complication", "Question", "Answer"]}]

    # 4. 保存文件
    with open("data/library.json", "w", encoding="utf-8") as f: json.dump(articles, f, ensure_ascii=False, indent=4)
    with open("data/books.json", "w", encoding="utf-8") as f: json.dump(books, f, ensure_ascii=False, indent=4)
    with open("data/models.json", "w", encoding="utf-8") as f: json.dump(models, f, ensure_ascii=False, indent=4)
    print("All data synced successfully.")

if __name__ == "__main__":
    run()
