import requests, feedparser, json, os, time
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
]

def ai_call(prompt, is_json=True):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "你是一位麦肯锡背景的精英教练。"}, {"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    if is_json: payload["response_format"] = {"type": "json_object"}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        return json.loads(content) if is_json else content
    except: return None

def run_sync():
    # 初始化结构，确保字段完整
    data = {
        "briefs": [], 
        "deep_articles": [], 
        "weekly_question": {"cn": "如何利用第一性原理重构竞争力？", "en": "How to leverage First Principles to rebuild competitiveness?"},
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # 如果已有数据则读取，保留 deep_articles
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)
                data["deep_articles"] = old_data.get("deep_articles", [])
                # 如果旧数据有提问也保留
                if "weekly_question" in old_data:
                    data["weekly_question"] = old_data["weekly_question"]
        except: pass

    print("📡 正在抓取快报...")
    for s in RSS_SOURCES:
        try:
            feed = feedparser.parse(s['url'])
            for item in feed.entries[:1]:
                data["briefs"].append({
                    "title": item.title, 
                    "link": item.link, 
                    "source": s['name'],
                    "time": datetime.now().strftime("%m-%d")
                })
        except: continue

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("✅ 同步完成")

if __name__ == "__main__":
    run_sync()
