import requests, feedparser, json, os, time
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 监控的全球智库源
RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG", "url": "https://www.bcg.com/rss.xml"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"}
]

def ai_analyze_content(title, link):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    # 深度解析 Prompt
    prompt = f"""Analyze the following business article: "{title}". 
    Return a JSON object with these EXACT keys:
    {{
        "en_summary": "A 3-sentence summary",
        "cn_summary": "3条核心中文洞察",
        "golden_sentences": [{{"en":"Quote", "cn":"中文金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example"}}],
        "case_study": "背景-决策-结果的深度分析",
        "reflection_flow": ["问题1: 关于布局", "问题2: 关于规划", "问题3: 落地动作"],
        "related_model": "思维模型名称",
        "scores": {{"Strategy": 80, "Leadership": 85, "Innovation": 70, "Insight": 90, "Decision": 75}}
    }}"""

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a top-tier business coach for Read & Rise."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except Exception as e:
        print(f"Error analyzing {title}: {e}")
        return None

def sync():
    print(f"🕒 {datetime.now()}: Starting daily sync...")
    data = {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "如何应对不确定性？", "en": "How to handle uncertainty?"}}
    
    # 尝试加载旧数据以保留“深度喂养”的文章
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            old = json.load(f)
            data["deep_articles"] = old.get("deep_articles", [])
            data["weekly_question"] = old.get("weekly_question", data["weekly_question"])

    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze_content(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
                print(f"✅ Synced: {s['name']}")
    
    data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    sync()
