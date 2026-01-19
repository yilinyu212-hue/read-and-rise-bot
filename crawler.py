import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    
    # 强制标签化与中英双语
    prompt = f"""作为企业家顾问，解析文章: '{title}'。
    必须返回如下严格JSON格式(双大括号转义):
    {{{{
        "en_summary": "150-word English executive summary.",
        "cn_analysis": "300字中文深度拆解(包含战略/创新/执行维度)。",
        "reading_level": "Level: Strategic (高阶)",
        "tags": ["AI", "Management", "Global"],
        "reflection_flow": ["问题1: ...", "问题2: ..."],
        "action_points": ["建议1: ...", "建议2: ..."],
        "model_scores": {{"战略": 90, "创新": 85, "执行": 70}}
    }}}}"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": 0.3
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except: return None

async def generate_audio(text):
    # 生成磁性男声伦敦腔
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save("daily_briefing.mp3")

def run_sync():
    print("🚀 Read & Rise 数据中枢运行中...")
    books = []
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                books = json.load(f).get("books", [])
        except: pass

    data = {"briefs": [], "books": books, "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
    
    if data["briefs"]:
        script = "Hi Leaders! Welcome to Read and Rise. Today we have top insights from McKinsey and HBR. Let's start."
        asyncio.run(generate_audio(script))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
