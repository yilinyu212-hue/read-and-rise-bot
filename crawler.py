import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 10个顶级信源 + 5本名著
RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"},
    {"name": "FastCompany", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "Strategy+Biz", "url": "https://www.strategy-business.com/rss"},
    {"name": "Aeon", "url": "https://aeon.co/feed.rss"},
    {"name": "TechCrunch", "url": "https://feedpress.me/techcrunch"}
]

RECOMMENDED_BOOKS = ["High Output Management", "Principles", "Thinking, Fast and Slow", "Atomic Habits", "The Lean Startup"]

def ai_analyze(title, content_type="Article"):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    
    # 核心修复：使用双大括号逃逸 f-string
    prompt = f"""Analyze this {content_type}: '{title}'. 
    Return a STRICT JSON:
    {{{{
        "en_title": "{title}",
        "cn_title": "中文标题",
        "en_summary": "150-word executive summary.",
        "cn_analysis": "300字中文深度拆解。",
        "case_study": "关联案例",
        "reflection": ["反思1", "反思2"],
        "model": "关联思维模型",
        "vocab": [{{"w": "word", "m": "含义", "e": "example"}}]
    }}}}"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

async def generate_audio(text, filename):
    try:
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
        await communicate.save(filename)
    except: pass

def run_sync():
    data = {"items": [], "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    # 同时处理书和文章
    for i, book in enumerate(RECOMMENDED_BOOKS):
        res = ai_analyze(book, "Book")
        if res:
            fn = f"audio_b_{i}.mp3"
            asyncio.run(generate_audio(res['en_summary'], fn))
            res["audio_file"] = fn
            data["items"].append(res)

    for i, s in enumerate(RSS_SOURCES):
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, "Article")
            if res:
                fn = f"audio_a_{i}.mp3"
                asyncio.run(generate_audio(res['en_summary'], fn))
                res["audio_file"] = fn
                res["source"] = s['name']
                data["items"].append(res)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
