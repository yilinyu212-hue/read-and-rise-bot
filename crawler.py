import os, requests, json, feedparser, uuid, time
from datetime import datetime

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def ask_ai(prompt):
    if not API_KEY: 
        print("Error: No API Key found.")
        return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are an Elite Business Educator. Output strictly in valid JSON."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res_json = res.json()
        # 增加防御性检查
        if "choices" in res_json:
            return json.loads(res_json['choices'][0]['message']['content'])
        else:
            print(f"DeepSeek API Error: {res_json}")
            return None
    except Exception as e:
        print(f"Network Error: {e}")
        return None

def run():
    os.makedirs("data", exist_ok=True)
    
    # 增加更多源，提高成功率
    SOURCES = [
        ("HBR", "https://hbr.org/rss/topic/leadership"),
        ("McKinsey", "https://www.mckinsey.com/insights/rss")
    ]
    
    articles = []
    for source_name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                prompt = f"Analyze: '{entry.title}'. JSON: {{'title':'{entry.title}','source':'{source_name}','en_excerpt':'...','cn_translation':'...','insight':'...','output_playbook':{{'speaking':'...'}},'logic_flow':['A','B']}}"
                res = ask_ai(prompt)
                if res:
                    res.update({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%m-%d")})
                    articles.append(res)
        except: continue

    # 强制生成书籍数据，确保不为空
    books = [
        {"title": "The Pyramid Principle", "intro": "Logical thinking gold standard.", "takeaways": ["Group ideas", "Top-down"], "coach_tips": "Focus on the governing thought."}
    ]

    with open("data/library.json", "w", encoding="utf-8") as f: json.dump(articles, f, ensure_ascii=False, indent=4)
    with open("data/books.json", "w", encoding="utf-8") as f: json.dump(books, f, ensure_ascii=False, indent=4)
    with open("data/models.json", "w", encoding="utf-8") as f: json.dump([{"name":"SCQA","scenario":"Pitch","coach_tips":"Start with context"}], f, ensure_ascii=False, indent=4)
    print(f"Successfully synced {len(articles)} articles.")

if __name__ == "__main__":
    run()
