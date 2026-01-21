import json, requests, os
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"

INPUT_FILE = "data/articles_raw.json"
OUTPUT_FILE = "data/data.json"
HISTORY_FILE = "data/knowledge_base.json"

PROMPT = """
You are a senior editor and management analyst.

Analyze the following article.

Return STRICT JSON:
{
  "cn_title": "",
  "cn_analysis": "",
  "mental_model": "",
  "en_summary": ""
}
"""

def analyze(article):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{
            "role": "user",
            "content": PROMPT + "\n\n" + article["title"] + "\n" + article["content"]
        }],
        "response_format": {"type": "json_object"}
    }

    res = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    return json.loads(res.json()["choices"][0]["message"]["content"])

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    results = []
    for art in articles:
        ai = analyze(art)
        results.append({
            **ai,
            "source": art["source"],
            "url": art["url"],
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"items": results}, f, ensure_ascii=False, indent=2)

    if os.path.exists(HISTORY_FILE):
        history = json.load(open(HISTORY_FILE, "r", encoding="utf-8"))
    else:
        history = []

    history = results + history
    json.dump(history, open(HISTORY_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("AI analysis completed.")

if __name__ == "__main__":
    main()
