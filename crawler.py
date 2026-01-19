import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 扩充抓取源
RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    
    # 修正大括号转义，并要求中英双语
    prompt = f"""Analyze this article: '{title}'. 
    Must return a strict JSON format with exactly these keys:
    {{
        "en_summary": "One paragraph English executive summary.",
        "cn_analysis": "300字中文深度决策解析。",
        "actions": ["Action 1", "Action 2", "Action 3"],
        "model_scores": {{"Strategy": 90, "Innovation": 80, "Execution": 85}}
    }}"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", 
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

async def generate_audio(text):
    # 使用 RyanNeural (BBC 风格)
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save("daily_briefing.mp3")

def run_sync():
    print("🚀 启动 Read & Rise 多源同步...")
    books = []
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                books = json.load(f).get("books", [])
        except: pass

    data = {"briefs": [], "books": books, "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    # 多源抓取
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res.update({"source": s['name'], "title": feed.entries[0].title, "link": feed.entries[0].link})
                data["briefs"].append(res)
                print(f"✅ 已入库: {s['name']}")
    
    # 生成 BBC 音频
    if data["briefs"]:
        script_text = f"Hi Leaders! Today's briefings cover {len(data['briefs'])} insights from McKinsey, HBR and more. Let's dive in."
        asyncio.run(generate_audio(script_text))
        print("🎙️ 语音播报已更新")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
