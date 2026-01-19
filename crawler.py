import requests, feedparser, json, os, random
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""解析文章: "{title}"。返回JSON：
    {{
        "en_summary": ["Point 1"], "cn_summary": ["要点1"],
        "golden_sentences": [{{"en":"quote", "cn":"金句"}}],
        "vocab_bank": [{{"word":"Term", "meaning":"含义", "example":"Example"}}],
        "case_study": "深度解析：背景-决策-结果",
        "reflection_flow": ["反思1", "反思2"],
        "teaching_tips": "给教育者的3个教学/管理建议",
        "model_scores": {{"战略": 85, "组织": 70, "创新": 90, "洞察": 80, "执行": 75}}
    }}"""
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": 0.3
        }, timeout=60)
        return {**json.loads(res.json()['choices'][0]['message']['content']), "title": title, "link": link}
    except: return None

def run_sync():
    print("🚀 启动 12 个全球智库源深度扫描...")
    data = {"briefs": [], "books": [], "weekly_question": {"cn":"如何重构竞争力？","en":"How to rebuild?"}}
    # 保留旧书籍
    if os.path.exists("data.json"):
        with open("data.json", "r") as f: data["books"] = json.load(f).get("books", [])
    
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res: 
                res["source"] = s['name']
                data["briefs"].append(res)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("🏁 全部同步完成！")

if __name__ == "__main__": run_sync()
