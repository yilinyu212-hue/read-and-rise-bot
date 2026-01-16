import os, requests, json, feedparser, uuid
from datetime import datetime

# 获取 API Key
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

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
    
    # 1. 抓取外刊
    print("Processing Articles...")
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    articles = []
    for e in feed.entries[:3]:
        res = ask_ai(f"Analyze article: '{e.title}'. Output JSON: {{'title':'{e.title}','source':'HBR','en_excerpt':'100 words','cn_translation':'翻译','vocabulary_pro':'word:mean','insight':'避坑指南','output_playbook':{{'speaking':'phrase'}},'logic_flow':['A','B','C']}}")
        if res:
            res.update({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%m-%d")})
            articles.append(res)
    
    # 2. 抓取/生成思维模型
    print("Processing Models...")
    models = []
    for m in ["MECE Principle", "SCQA Framework"]:
        res_m = ask_ai(f"Analyze model: '{m}'. Output JSON: {{'name':'{m}','scenario':'场景','coach_tips':'避坑指南','logic_flow':['Step1','Step2']}}")
        if res_m: models.append(res_m)

    # 3. 抓取/生成书籍推荐
    print("Processing Books...")
    books = []
    for b in ["The Pyramid Principle", "Atomic Habits"]:
        res_b = ask_ai(f"Summarize book: '{b}'. Output JSON: {{'title':'{b}','intro':'简介','takeaways':['A','B'],'coach_tips':'高管阅读建议'}}")
        if res_b: books.append(res_b)

    # 保存全量数据
    with open("data/library.json", "w", encoding="utf-8") as f: json.dump(articles, f, ensure_ascii=False, indent=4)
    with open("data/models.json", "w", encoding="utf-8") as f: json.dump(models, f, ensure_ascii=False, indent=4)
    with open("data/books.json", "w", encoding="utf-8") as f: json.dump(books, f, ensure_ascii=False, indent=4)
    print("Sync Completed.")

if __name__ == "__main__":
    run()
