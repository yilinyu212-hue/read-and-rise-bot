import requests, feedparser, json, os, time
from datetime import datetime

# ================= 1. 配置中心 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
]

# ================= 2. AI 解析引擎 =================
def ai_deep_analyze(title, link):
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""解析文章: "{title}"。必须返回严格JSON格式：
    {{
        "en_summary": ["English Point 1", "Point 2"],
        "cn_summary": ["中文要点1", "要点2"],
        "golden_sentences": [{{"en":"quote", "cn":"金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example"}}],
        "case_study": "背景-决策-结果解析",
        "reflection_flow": ["反思1", "反思2"],
        "related_model": "思维模型名称"
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

# ================= 3. 主程序 =================
def run_sync():
    print(f"🚀 开始扫描全球智库...")
    data = {
        "briefs": [], 
        "weekly_question": {
            "cn": "面对 2026 的挑战，如何通过‘第一性原理’重构核心竞争力？", 
            "en": "How to leverage First Principles to rebuild competitiveness?"
        },
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_deep_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
                print(f"✅ 解析成功: {s['name']}")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("🏁 全部同步完成！")

if __name__ == "__main__":
    run_sync()
