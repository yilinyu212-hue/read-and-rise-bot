import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 顶级信源库
RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    
    # 修复：JSON 格式使用双大括号 {{ }} 避免 f-string 报错
    prompt = f"""As a top business consultant, analyze this article: '{title}'. 
    Return a strict JSON object:
    {{
        "en_summary": "A 100-word executive summary in English.",
        "cn_analysis": "300字中文深度拆解：包含行业影响、竞争策略及教育者启示。",
        "actions": ["Action Point 1", "Action Point 2", "Action Point 3"],
        "model_scores": {{"Strategy": 90, "Innovation": 85, "Execution": 75, "Insight": 95}}
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

async def generate_audio(text):
    # 使用 Edge-TTS 生成极具质感的伦敦腔
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save("daily_briefing.mp3")

def run_sync():
    print("🚀 正在从全球顶级信源同步情报...")
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
            # 抓取每个源最新的那篇文章
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
                print(f"✅ 已抓取: {s['name']}")
    
    if data["briefs"]:
        script = f"Good day. This is your Read and Rise daily briefing. We've analyzed the latest from McKinsey, HBR, and The Economist. Let's look at today's strategic shifts."
        asyncio.run(generate_audio(script))
        print("🎙️ 语音播报合成完成")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
