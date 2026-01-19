import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss"}
]

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    # 使用占位符避免 f-string 大括号冲突
    raw_prompt = """
    You are an AI Mentor for Educators & Leaders. Analyze the article: '{title}'.
    Return a STRICT JSON object with these keys:
    "cn_title" (attractive chinese title), 
    "en_title" (original title),
    "en_summary" (A 120-word deep professional English summary for audio training),
    "cn_analysis" (300-word deep chinese analysis),
    "case_study" (practical management case),
    "reflection_flow" (list of 2 questions),
    "vocab_cards" (list of 2 word/meaning objects).
    """
    prompt = raw_prompt.replace("{title}", title)
    
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat", 
            "messages": [{"role": "user", "content": prompt}], 
            "response_format": {"type": "json_object"}
        }
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return None

async def gen_voice(text, filename):
    try:
        # Ryan 是深沉的英音男声，适合领导力内容
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
        await communicate.save(filename)
    except: pass

def main():
    all_data = []
    for i, s in enumerate(RSS_SOURCES):
        feed = feedparser.parse(s['url'])
        if feed.entries:
            # 抓取每个来源的第一篇文章，确保多来源
            entry = feed.entries[0]
            print(f"Processing: {entry.title}")
            content = ai_analyze(entry.title)
            if content:
                item = json.loads(content)
                audio_fn = f"audio_{i}.mp3"
                # 朗读 120 字的深度摘要，时长约 50-70 秒
                asyncio.run(gen_voice(item.get('en_summary', entry.title), audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
