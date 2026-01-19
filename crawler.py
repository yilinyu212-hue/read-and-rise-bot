import requests, feedparser, json, os, random
from datetime import datetime

# 环境变量
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""作为教育智库专家解析文章: "{title}"。必须返回严格 JSON：
    {{
        "en_summary": ["Point 1", "Point 2"],
        "cn_summary": ["要点1", "要点2"],
        "golden_sentences": [{{"en":"quote", "cn":"金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example"}}],
        "case_study": "背景-决策-结果深度解析",
        "reflection_flow": ["反思问题1", "反思问题2"],
        "teaching_tips": "给教育者的3个落地应用建议",
        "model_scores": {{"战略": 85, "组织": 70, "创新": 90, "洞察": 80, "执行": 75}}
    }}"""
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": 0.3
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except: return None

def run_sync():
    # 保留旧书
    existing_books = []
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            existing_books = json.load(f).get("books", [])

    data = {"briefs": [], "books": existing_books, "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
