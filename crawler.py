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
    # 使用 double braces {{ }} 避开 f-string 报错
    prompt = f"""
    You are an AI Mentor for Educators & Leaders. Analyze the article: '{title}'.
    Return a STRICT JSON object:
    {{
        "cn_title": "中文深度标题",
        "en_title": "{title}",
        "en_summary": "Write a 100-word professional English summary. This text will be used for a 1-minute audio training. Focus on leadership insights.",
        "cn_analysis": "300字中文教练视角拆解：Read (输入) & Rise (领导力认知提升)。",
        "case_study": "一个具体的管理/教学实战案例。",
        "reflection_flow": ["反思建议1", "反思建议2"],
        "vocab_cards": [{{"word": "Keyword", "meaning": "地道管理/教育用法"}}]
    }}"""
    
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error analyzing {title}: {e}")
        return None

async def gen_voice(text, filename):
    try:
        # 使用 RyanNeural 朗读整段摘要，长度将显著增加
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
                # 朗读 100 字摘要，时长约 45-60 秒
                asyncio.run(gen_voice(item.get('en_summary', entry.title), audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
