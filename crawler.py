import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 10个顶级外刊信源
RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss"},
    {"name": "Aeon", "url": "https://aeon.co/feed.rss"},
    {"name": "TechCrunch", "url": "https://feedpress.me/techcrunch"}
]

# 5本必读管理学名著
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
    
    # 使用双大括号 escaping 解决 Invalid format specifier 报错
    prompt = f"""As a business mentor, analyze this {type}: '{content_title}'. 
    Return a STRICT JSON:
    {{{{
        "en_title": "{content_title}",
        "cn_title": "中文标题",
        "reading_level": "Senior/Mid/Entry",
        "en_summary": "150-word summary in English.",
        "cn_analysis": "300字中文深度拆解(含战略意义)。",
        "case_study": "本内容关联的实际案例拆解",
        "reflection_flow": ["反思问题1", "反思问题2"],
        "mental_model": "关联的一个管理学思维模型",
        "vocab_cards": [
            {{"word": "word", "meaning": "中文含义", "example": "Eng sentence"}}
        ]
    }}}}"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": 0.3
        }, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

async def generate_voice(text, filename):
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save(filename)

def run_sync():
    data = {"items": [], "books": [], "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    # 1. 处理书籍精华
    for i, book in enumerate(RECOMMENDED_BOOKS):
        res = ai_analyze(book, type="Book")
        if res:
            audio_fn = f"audio_book_{i}.mp3"
            asyncio.run(generate_voice(res['en_summary'], audio_fn))
            res["audio_file"] = audio_fn
            data["items"].append(res)

    # 2. 处理外刊新闻
    for i, s in enumerate(RSS_SOURCES):
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, type="Article")
            if res:
                res["source"] = s['name']
                audio_fn = f"audio_art_{i}.mp3"
                asyncio.run(generate_voice(res['en_summary'], audio_fn))
                res["audio_file"] = audio_fn
                data["items"].append(res)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
