import requests, feedparser, json, os, time, random
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 🌍 15+ 全球顶级智库与商业源
RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "BCG", "url": "https://www.bcg.com/rss.xml"},
    {"name": "Knowledge@Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    {"name": "Stanford eCorner", "url": "https://ecorner.stanford.edu/feed/"},
    {"name": "Wired", "url": "https://www.wired.com/feed/category/business/latest/rss"},
    {"name": "World Economic Forum", "url": "https://www.weforum.org/agenda/feed"}
]

QUESTION_POOL = [
    {"cn": "如果用‘第一性原理’重构你的产品，你会删掉哪个功能？", "en": "If you rebuilt your product using 'First Principles', which feature would you remove?"},
    {"cn": "面对 2026 的剧变，你的布局是否具备‘反脆弱’特征？", "en": "Does your layout possess 'anti-fragile' characteristics?"},
    {"cn": "你目前的决策，是基于‘过去经验’还是‘未来趋势’？", "en": "Is your current decision based on 'past experience' or 'future trends'?"}
]

def ai_analyze(title, link):
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""作为 AI 教练解析文章: "{title}"。返回严格 JSON 格式：
    {{
        "en_summary": ["Point 1", "Point 2"],
        "cn_summary": ["中文要点1", "要点2"],
        "golden_sentences": [{{"en":"quote", "cn":"金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example"}}],
        "case_study": "深度解析：背景-决策-结果",
        "reflection_flow": ["反思1", "反思2"],
        "related_model": "模型名称",
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
    data = {"briefs": [], "books": [], "weekly_question": random.choice(QUESTION_POOL), "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                old = json.load(f)
                data["books"] = old.get("books", []) # 保留书籍库
        except: pass
    
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
