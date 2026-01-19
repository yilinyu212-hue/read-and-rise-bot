import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 10个顶级信源 + 5本核心书籍
RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "TechCrunch", "url": "https://feedpress.me/techcrunch"},
    {"name": "Aeon", "url": "https://aeon.co/feed.rss"}, # 深度哲学/行为
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss"}
]

RECOMMENDED_BOOKS = [
    "High Output Management by Andy Grove",
    "Principles by Ray Dalio",
    "Thinking, Fast and Slow by Daniel Kahneman",
    "Atomic Habits by James Clear",
    "The Lean Startup by Eric Ries"
]

def ai_analyze(content_title, type="article"):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    
    prompt = f"""As a business mentor, analyze this {type}: '{content_title}'. 
    Return a STRICT JSON (double curly braces):
    {{{{
        "en_title": "{content_title}",
        "cn_title": "中文标题",
        "type": "{type}",
        "en_summary": "150-word executive summary.",
        "cn_analysis": "300字中文深度拆解(含战略意义)。",
        "case_study": "本内容关联的商业/实际案例拆解",
        "reflection_flow": ["反思问题1", "反思问题2"],
        "vocab_cards": [
            {{"word": "word", "phonetic": "/.../", "meaning": "含义", "example": "sentence"}}
        ],
        "audio_script": "A clear, natural reading script for this summary."
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
    data = {"items": [], "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    # 处理书籍 (Highly Recommended)
    print("📚 正在生成书籍精华...")
    for book in RECOMMENDED_BOOKS:
        res = ai_analyze(book, type="Book")
        if res:
            audio_fn = f"audio_book_{RECOMMENDED_BOOKS.index(book)}.mp3"
            asyncio.run(generate_voice(res['audio_script'], audio_fn))
            res["audio_file"] = audio_fn
            data["items"].append(res)

    # 处理外刊 (Top 10 Sources)
    print("🚀 正在同步全球外刊...")
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, type="Article")
            if res:
                res["source"] = s['name']
                audio_fn = f"audio_art_{RSS_SOURCES.index(s)}.mp3"
                asyncio.run(generate_voice(res['audio_script'], audio_fn))
                res["audio_file"] = audio_fn
                data["items"].append(res)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
