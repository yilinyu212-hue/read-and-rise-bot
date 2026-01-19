import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

# 配置 API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 10个顶级信源
RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"},
    {"name": "FastCompany", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "Aeon", "url": "https://aeon.co/feed.rss"},
    {"name": "TechCrunch", "url": "https://feedpress.me/techcrunch"},
    {"name": "Strategy+Biz", "url": "https://www.strategy-business.com/rss"}
]

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""As a mentor for educators, analyze: '{title}'. 
    Return STRICT JSON:
    {{
        "cn_title": "中文标题",
        "en_title": "{title}",
        "cn_analysis": "300字深度摘要",
        "case_study": "针对教育/管理者的实际应用案例",
        "mental_model": "思维模型名称",
        "reflection_flow": ["反思提问1", "反思提问2"],
        "vocab_cards": [{"word": "单词", "meaning": "含义"}]
    }}"""
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, 
                           json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}})
        return res.json()['choices'][0]['message']['content']
    except: return None

async def gen_voice(text, filename):
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save(filename)

def main():
    all_data = []
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            content = ai_analyze(feed.entries[0].title)
            if content:
                item = json.loads(content)
                audio_fn = f"audio_{RSS_SOURCES.index(s)}.mp3"
                asyncio.run(gen_voice(item['en_title'], audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data, "update_time": datetime.now().strftime("%Y-%m-%d")}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
