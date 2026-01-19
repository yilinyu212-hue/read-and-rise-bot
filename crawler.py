import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    
    # 定义严格的 JSON 结构，包含单词和模型
    prompt = f"""As a business mentor, analyze: '{title}'. 
    Return a strict JSON format (double curly braces):
    {{{{
        "en_title": "{title}",
        "cn_title": "中文标题",
        "reading_level": "B2/C1 (Strategic)",
        "en_summary": "150-word English summary.",
        "cn_analysis": "300字中文深度拆解。",
        "mental_model": {{"name": "思维模型名称", "logic": "该模型如何应用到此案例"}},
        "vocabulary": [
            {{"word": "word1", "phonetic": "/.../", "meaning": "中文", "example": "Eng sentence"}}
        ],
        "reflection": ["Reflection 1", "Reflection 2"]
    }}}}"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

async def generate_voice(text, filename):
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save(filename)

def run_sync():
    print("🏹 Read & Rise 工厂启动...")
    data = {"briefs": [], "books": [], "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data["books"] = json.load(f).get("books", [])
        except: pass

    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                # 为每篇文章生成单独的语音文件名（可选，此处先生成全局简报）
                data["briefs"].append(res)
    
    if data["briefs"]:
        # 生成全局简报音频
        full_text = " . ".join([b['en_summary'] for b in data['briefs'][:2]])
        asyncio.run(generate_voice(full_text, "daily_briefing.mp3"))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
