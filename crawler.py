import requests, feedparser, json, os, time
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
]

def ai_analyze(title, link):
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""深度解析商业文章: "{title}"。
    必须返回 JSON：
    {{
        "en_summary": ["Point 1", "Point 2"],
        "cn_summary": ["中文要点1", "中文要点2"],
        "golden_sentences": [{{"en":"Quote", "cn":"金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example"}}],
        "case_study": "背景-决策-结果解析",
        "reflection_flow": ["反思1", "反思2"],
        "related_model": "思维模型"
    }}"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except: return None

def run_sync():
    # 1. 结构初始化，防止主页 KeyError
    data = {
        "briefs": [], 
        "deep_articles": [], 
        "weekly_question": {
            "cn": "面对 2026 的不确定性，你的布局是否具备‘反脆弱’特征？", 
            "en": "Does your layout possess 'anti-fragile' characteristics for 2026?"
        },
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # 2. 抓取逻辑
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
                print(f"✅ 已解析: {s['name']}")

    # 3. 保存
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
