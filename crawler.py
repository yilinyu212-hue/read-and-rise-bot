import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

# 环境变量读取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: 
        return None
    url = "https://api.deepseek.com/chat/completions"
    
    # 修正点：JSON 的大括号必须使用 {{ }} 转义，否则会报 Invalid format specifier
    prompt = f"""作为顶级商业顾问解析文章: '{title}'。必须返回严格的 JSON 格式：
    {{
        "cn_summary": ["3条要点"],
        "case_study": "案例解析",
        "reflection_flow": ["深度提问"],
        "vocab_bank": [{{"word":"Term","meaning":"含义","example":"例句"}}],
        "model_scores": {{"战略":85,"创新":80,"洞察":90,"组织":70,"执行":75}}
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

async def generate_audio(text):
    # 使用 RyanNeural (BBC 风格伦敦腔)
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save("daily_briefing.mp3")

def run_sync():
    print("🚀 开始数据同步...")
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
        titles = " | ".join([b['title'] for b in data['briefs'][:3]])
        script_prompt = f"Act as a BBC anchor. Summarize these in 150 words: {titles}. Start with 'Hi, Leaders! This is your Read and Rise daily briefing.'"
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": script_prompt}]})
        script = res.json()['choices'][0]['message']['content']
        asyncio.run(generate_audio(script))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
