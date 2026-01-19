import requests, feedparser, json, os
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 12个顶级源
RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    # ... 其他10个源 ...
]

def ai_call(prompt, is_json=True):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "你是一位拥有麦肯锡背景的商业教练。"}, {"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    if is_json: payload["response_format"] = {"type": "json_object"}
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        return json.loads(content) if is_json else content
    except: return None

def run_rss_sync():
    # 爬虫逻辑：仅抓取标题和链接，做简单的中英总结
    print("📡 开启爬虫快报同步...")
    data = {"briefs": [], "deep_articles": [], "weekly_question": {}, "update_time": ""}
    # 如果文件已存在，先读取保留 deep_articles
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    new_briefs = []
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        for item in feed.entries[:1]: # 每个源抓一条
            summary_prompt = f"Summarize this title in 1 sentence (Bilingual): {item.title}"
            summary = ai_call(summary_prompt, is_json=False)
            new_briefs.append({"title": item.title, "link": item.link, "source": s['name'], "summary": summary})
    
    data["briefs"] = new_briefs
    data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_rss_sync()
