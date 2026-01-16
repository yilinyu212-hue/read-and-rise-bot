import os, requests, json, feedparser, uuid
from datetime import datetime

# 从 GitHub Secrets 获取 Key
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def get_structured_ai_data(prompt):
    if not API_KEY:
        print("ERROR: API KEY NOT FOUND")
        return None
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are an Elite Business Coach. Always output valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        data = res.json()
        if "choices" in data:
            return json.loads(data['choices'][0]['message']['content'])
        else:
            print(f"API FAILURE: {data}") # 这样能在 Action 日志里看到具体错误
            return None
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return None

def run():
    # 抓取逻辑
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    articles = []
    
    if feed.entries:
        for e in feed.entries[:3]:
            print(f"Analyzing: {e.title}")
            prompt = f"Deconstruct this title into a professional English lesson JSON: '{e.title}'. Include fields: title, level, en_excerpt, cn_translation, vocabulary_pro (word:mean format), syntax_analysis, logic_flow (list of 3 steps), output_playbook (dict with speaking/writing)."
            res = get_structured_ai_data(prompt)
            if res:
                res.update({"date": datetime.now().strftime("%Y-%m-%d"), "source": "HBR"})
                articles.append(res)
    
    # 只有抓取到内容才写入，防止把旧数据覆盖成空的
    if articles:
        os.makedirs("data", exist_ok=True)
        with open("data/library.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        print("Successfully updated data/library.json")

if __name__ == "__main__":
    run()
