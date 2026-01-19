import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

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
    # 使用 double-brace {{ }} 避开 f-string 解析冲突
    prompt = f"""
    You are an AI assistant for an Executive Coach & English Trainer. 
    Analyze: '{title}'. 
    Slogan: Read to Rise, Rise to Lead.
    
    Return STRICT JSON:
    {{
        "cn_title": "中文标题",
        "en_title": "{title}",
        "cn_analysis": "300字教练视角摘要",
        "case_study": "实战管理案例",
        "reflection_flow": ["反思提问1", "反思提问2"],
        "vocab_cards": [{{"word": "Key Term", "meaning": "地道用法"}}],
        "mental_model": "思维模型"
    }}"""
    
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return None

async def gen_voice(text, filename):
    try:
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
        await communicate.save(filename)
    except: pass

def main():
    all_data = []
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
    
    # 强制保存为带有 "items" 键的字典格式，修复 get() 报错
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
