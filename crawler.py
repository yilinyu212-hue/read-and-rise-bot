import requests, feedparser, json, os, time
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG", "url": "https://www.bcg.com/rss.xml"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "Knowledge@Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss/all_articles"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
    {"name": "Wired", "url": "https://www.wired.com/feed/category/business/latest/rss"}
]

def ai_analyze_content(title, link):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    prompt = f"""Analyze the business article: "{title}". 
    Return a JSON object: {{
        "en_summary": "3 bullet points summary in English",
        "cn_summary": "3条核心中文摘要",
        "golden_sentences": [{{"en":"Quote", "cn":"金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example sentence"}}],
        "case_study": "背景-决策-结果深度解析",
        "reflection_flow": ["Reflection Q", "Action Advice"],
        "related_model": "Mental Model Name",
        "scores": {{"Strategy": 85, "Leadership": 80, "Innovation": 90, "Insight": 85, "Decision": 80}}
    }}"""
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a McKinsey-style coach."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except: return None

def run_sync():
    data = {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "如何利用第一性原理重构竞争力？", "en": "How to leverage First Principles to rebuild competitiveness?"}, "update_time": ""}
    # 尝试保留现有的深度上传文章
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                old = json.load(f)
                data["deep_articles"] = old.get("deep_articles", [])
        except: pass

    print("🚀 启动全球智库深度扫描...")
    for s in RSS_SOURCES:
        try:
            feed = feedparser.parse(s['url'])
            if feed.entries:
                item = feed.entries[0]
                res = ai_analyze_content(item.title, item.link)
                if res:
                    res["source"] = s['name']
                    data["briefs"].append(res)
                    print(f"✅ 已解析: {s['name']}")
                time.sleep(1)
        except: continue

    data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("🏁 全部同步完成！数据已更新。")

if __name__ == "__main__":
    run_sync()
