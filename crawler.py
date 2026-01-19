import requests, feedparser, json, os, time
from datetime import datetime

# ================= 1. 配置区 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG Global Insights", "url": "https://www.bcg.com/rss.xml"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Financial Times", "url": "https://www.ft.com/management?format=rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Knowledge at Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss/all_articles"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
    {"name": "Wired Business", "url": "https://www.wired.com/feed/category/business/latest/rss"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/category/enterprise/feed/"}
]

# ================= 2. 深度解析逻辑 =================
def ai_analyze_content(title, link, mode="brief"):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""
    Analyze the business article: "{title}".
    Requirement: Return a JSON object with:
    1. "en_summary": 3 bullet points summary in English.
    2. "cn_summary": 3条中文摘要.
    3. "golden_sentences": [{"en":"...", "cn":"..."}] (2 quotes).
    4. "vocab_bank": [{"word":"...", "meaning":"...", "example":"..."}] (3 business terms).
    5. "case_study": "背景-决策-结果的深度解析".
    6. "reflection_flow": ["Reflection Question", "Actionable Advice"].
    7. "related_model": "Matching Mental Model Name",
    8. "scores": {{"Strategy": 85, "Leadership": 80, "Innovation": 90, "Insight": 85, "Decision": 80}}
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a McKinsey-style business coach."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except:
        return None

def run_sync():
    data = {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "如何重构竞争力？", "en": "How to rebuild?"}, "update_time": ""}
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            old = json.load(f)
            data["deep_articles"] = old.get("deep_articles", [])
            data["weekly_question"] = old.get("weekly_question", data["weekly_question"])

    print("📡 启动 12 个全球智库源深度扫描...")
    for s in RSS_SOURCES:
        try:
            feed = feedparser.parse(s['url'])
            for item in feed.entries[:1]: # 每个源抓最新一篇
                res = ai_analyze_content(item.title, item.link)
                if res:
                    res["source"] = s['name']
                    data["briefs"].append(res)
                    print(f"✅ 已解析: {s['name']}")
                time.sleep(1) # 减缓请求，防止腾讯云报警
        except: continue

    data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("🏁 全部同步完成！")

if __name__ == "__main__":
    run_sync()
