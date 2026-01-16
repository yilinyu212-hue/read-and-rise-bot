import os, requests, json, feedparser, uuid
from datetime import datetime

# 获取 API Key
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def ask_ai(prompt):
    if not DEEPSEEK_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
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
        return None
    except: return None

def run():
    os.makedirs("data", exist_ok=True)
    
    # 1. 抓取外刊 (HBR Leadership)
    print("Fetching HBR Articles...")
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    articles = []
    for e in feed.entries[:3]:
        # 这里的 Prompt 增加了“教练视角”和“避坑指南”
        prompt = f"""
        Analyze article: '{e.title}'. 
        Output JSON: {{
            "title": "Title",
            "source": "HBR",
            "en_excerpt": "100-word paragraph",
            "cn_translation": "Translation",
            "vocabulary_pro": "word:mean, word2:mean",
            "insight": "AI 抓不到的中国企业本土化落地难点或高管避坑指南",
            "output_playbook": {{"speaking": "10-second power phrase for Monday morning", "writing": "email template"}},
            "logic_flow": ["Step 1", "Step 2", "Step 3"]
        }}
        """
        res = ask_ai(prompt)
        if res:
            res.update({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%m-%d")})
            articles.append(res)
    
    # 2. 模拟思维模型 (确保 models.json 不再为空)
    models = []
    for m_name in ["MECE Principle", "SCQA Framework"]:
        m_prompt = f"Analyze model '{m_name}' for leaders. JSON: {{'name':'{m_name}','scenario':'Usage','coach_tips':'Tips','logic_flow':['A','B']}}"
        res_m = ask_ai(m_prompt)
        if res_m: models.append(res_m)

    # 3. 模拟书籍 (确保 books.json 不再为空)
    books = [{"title": "The Pyramid Principle", "intro": "Logical thinking for executives.", "logic_flow": ["Build Top", "Support Groups"]}]

    # 保存所有文件
    with open("data/library.json", "w", encoding="utf-8") as f: json.dump(articles, f, ensure_ascii=False, indent=4)
    with open("data/models.json", "w", encoding="utf-8") as f: json.dump(models, f, ensure_ascii=False, indent=4)
    with open("data/books.json", "w", encoding="utf-8") as f: json.dump(books, f, ensure_ascii=False, indent=4)
    print("All data updated.")

if __name__ == "__main__":
    run()
