import requests, feedparser, json, os, time
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
]

def ai_deep_analyze(title, link):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""作为首席 AI 教练，深度解析文章: "{title}"。
    必须返回 JSON 格式：
    {{
        "en_summary": ["Point 1", "Point 2", "Point 3"],
        "cn_summary": ["中文要点1", "中文要点2", "中文要点3"],
        "golden_sentences": [{{"en":"Quote", "cn":"金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example"}}],
        "case_study": "背景-决策-结果解析",
        "reflection_flow": ["反思问题1", "反思问题2", "实践建议"],
        "related_model": "思维模型"
    }}"""
    
    try:
        res = requests.post(url, headers=headers, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link, "source": "Insight"})
        return content
    except: return None

def run_sync():
    data = {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "如何布局未来？", "en": "How to layout?"}}
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                old = json.load(f)
                data["deep_articles"] = old.get("deep_articles", [])
        except: pass

    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_deep_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
    
    data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
