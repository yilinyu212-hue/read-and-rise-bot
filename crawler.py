import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"}
]

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    # 使用 {{ }} 避免 f-string 解析冲突
    prompt = f"""
    You are an Executive Coach & English Trainer. Analyze: '{title}'. 
    Return STRICT JSON:
    {{
        "cn_title": "吸引管理者的中文标题",
        "en_title": "{title}",
        "en_audio_summary": "A 3-sentence professional summary in English for leadership training.",
        "cn_analysis": "300字深度解析：Read (输入) & Rise (领导力认知)。",
        "case_study": "针对此趋势的企业实战管理案例。",
        "reflection_flow": ["反思问题1", "反思问题2"],
        "vocab_cards": [{{"word": "Keyword", "meaning": "地道管理表达"}}]
    }}"""
    
    try:
        res = requests.post(url, 
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, 
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
                # 朗读 3 句长的英文摘要，不再只是朗读标题
                asyncio.run(gen_voice(item.get('en_audio_summary', feed.entries[0].title), audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
