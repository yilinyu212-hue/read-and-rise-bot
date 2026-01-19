import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

# 获取 API KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 10个顶级外刊信源
RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss"},
    {"name": "Aeon", "url": "https://aeon.co/feed.rss"},
    {"name": "TechCrunch", "url": "https://feedpress.me/techcrunch"}
]

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    # 注意：JSON的大括号必须双写 {{ }} 才能在 f-string 中正常显示
    prompt = f"""As a mentor for educators, analyze: '{title}'. 
    Return STRICT JSON:
    {{
        "cn_title": "中文标题",
        "en_title": "{title}",
        "cn_analysis": "300字深度洞察摘要",
        "case_study": "针对教育/机构管理者的实际应用案例",
        "mental_model": "思维模型名称",
        "reflection_flow": ["反思提问1", "反思提问2"]
    }}"""
    
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat", 
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI Error: {e}")
        return None

async def gen_voice(text, filename):
    try:
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
        await communicate.save(filename)
    except: pass

def main():
    all_data = []
    print("🚀 Starting sync...")
    for i, s in enumerate(RSS_SOURCES):
        feed = feedparser.parse(s['url'])
        if feed.entries:
            entry = feed.entries[0]
            content = ai_analyze(entry.title)
            if content:
                item = json.loads(content)
                audio_fn = f"audio_{i}.mp3"
                asyncio.run(gen_voice(entry.title, audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data, "update_time": datetime.now().strftime("%Y-%m-%d")}, f, ensure_ascii=False)
    print("✅ Sync complete.")

if __name__ == "__main__":
    main()
