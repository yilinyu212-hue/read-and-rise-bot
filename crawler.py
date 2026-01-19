import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime
import time

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "Aeon", "url": "https://aeon.co/feed.rss"},
    {"name": "TechCrunch", "url": "https://feedpress.me/techcrunch"}
]

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    prompt_tpl = """Analyze: '{title}'. Return STRICT JSON:
    { "cn_title": "...", "en_summary": "120-word english...", "cn_analysis": "...", "mental_model": "...", "vocab_list": [], "case_study": "...", "reflection": [] }"""
    prompt = prompt_tpl.replace("{title}", title)
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, 
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return None

async def gen_voice(text, filename):
    try:
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
        await communicate.save(filename)
    except: pass

def main():
    new_items = []
    # 1. 尝试抓取 10 个源
    for i, s in enumerate(RSS_SOURCES):
        feed = feedparser.parse(s['url'])
        if feed.entries:
            entry = feed.entries[0]
            print(f"Processing {s['name']}...")
            content = ai_analyze(entry.title)
            if content:
                item = json.loads(content)
                item['date'] = datetime.now().strftime("%Y-%m-%d")
                item['source'] = s['name']
                audio_fn = f"audio_{i}.mp3"
                asyncio.run(gen_voice(item.get('en_summary', ''), audio_fn))
                item['audio_file'] = audio_fn
                new_items.append(item)
            time.sleep(1) # 避免触发 API 限制

    # 2. 实现归档逻辑 (Archive to Knowledge Base)
    history_file = "knowledge_base.json"
    history_data = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history_data = json.load(f)
    
    # 将新文章追加到历史库（去重逻辑：标题不同则加入）
    existing_titles = [x.get('cn_title') for x in history_data]
    for item in new_items:
        if item['cn_title'] not in existing_titles:
            history_data.insert(0, item)
    
    # 3. 保持 data.json 为最新的 10 篇，归档库保留所有
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": new_items}, f, ensure_ascii=False)
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
