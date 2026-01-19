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
    # 身份定制 Prompt
    prompt = f"""
    You are an AI assistant for an Executive Coach & English Trainer. 
    Analyze the article: '{title}'. 
    
    Target Slogan: Read to Rise, Rise to Lead.
    
    Return STRICT JSON:
    {{
        "cn_title": "吸引管理者的中文标题",
        "en_title": "{title}",
        "cn_analysis": "300字教练视角摘要：Read (输入了什么) & Rise (认知提升了什么)。",
        "case_study": "针对企业管理者的实战 Coaching Case。",
        "reflection_flow": ["基于此文的领导力反思1", "基于此文的领导力反思2"],
        "vocab_cards": [
            {{"word": "Key Business Term", "meaning": "地道含义及在领导力场景下的用法"}}
        ],
        "mental_model": "思维模型名称"
    }}"""
    
    try:
        res = requests.post(url, 
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}, 
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}},
            timeout=60)
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
            content = ai_analyze(feed.entries[0].title)
            if content:
                item = json.loads(content)
                audio_fn = f"audio_{i}.mp3"
                asyncio.run(gen_voice(feed.entries[0].title, audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data, "update_time": datetime.now().strftime("%Y-%m-%d")}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
