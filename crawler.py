import os, requests, json, feedparser, uuid
from datetime import datetime

# 配置环境
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are an Elite Executive Coach. Output strictly in JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        data = res.json()
        if "choices" in data:
            return json.loads(data['choices'][0]['message']['content'])
        else:
            print(f"API Reject: {data}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def run():
    os.makedirs("data", exist_ok=True)
    
    # 1. 外刊解析
    print("Fetching HBR...")
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    articles = []
    for e in feed.entries[:3]:
        prompt = f"""Deconstruct this article into a high-end educator's playbook: '{e.title}'. 
        Required JSON fields: title, source, en_excerpt, cn_translation, insight (AI 抓不到的本土落地难点), output_playbook (dict: speaking, writing)."""
        res = ask_ai(prompt)
        if res:
            res.update({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d")})
            articles.append(res)
    if articles:
        with open("data/library.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)

    # 2. 思维模型解析 (手动指定 3 个)
    models = []
    for m_name in ["MECE Principle", "SCQA Framework", "First Principles"]:
        prompt = f"Analyze mental model '{m_name}' for leaders. JSON: name, scenario, coach_tips (避坑指南)."
        res = ask_ai(prompt)
        if res: models.append(res)
    if models:
        with open("data/models.json", "w", encoding="utf-8") as f:
            json.dump(models, f, ensure_ascii=False, indent=4)

    # 3. 书籍解析
    books = []
    for b_name in ["The Pyramid Principle"]:
        prompt = f"Summarize book '{b_name}' for a 60-second audio script. JSON: title, brief."
        res = ask_ai(prompt)
        if res: books.append(res)
    if books:
        with open("data/books.json", "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
