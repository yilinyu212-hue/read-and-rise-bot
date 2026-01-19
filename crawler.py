import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"}
]

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""
    You are an Executive Coach & English Trainer. Analyze: '{title}'.
    Return STRICT JSON:
    {{
        "cn_title": "中文标题",
        "en_title": "{title}",
        "en_summary": "A 2-sentence English professional summary of this article for audio reading.",
        "cn_analysis": "300字深度中文教练视角分析。",
        "case_study": "针对管理者的实战应用案例。",
        "reflection_flow": ["反思问题1", "反思问题2"],
        "vocab_cards": [{{"word": "Key Term", "meaning": "地道用法"}}]
    }}"""
    try:
        res = requests.post(url, 
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, 
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}},
            timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return None

async def gen_voice(text, filename):
    # 现在朗读的是 en_summary（摘要），而不是标题，时长会增加到 20-30 秒
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save(filename)

def main():
    all_data = []
    for i, s in enumerate(RSS_SOURCES):
        feed = feedparser.parse(s['url'])
        if feed.entries:
            entry = feed.entries[0]
            content_str = ai_analyze(entry.title)
            if content_str:
                item = json.loads(content_str)
                audio_fn = f"audio_{i}.mp3"
                # 使用英文摘要生成语音
                asyncio.run(gen_voice(item.get('en_summary', entry.title), audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
