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
    # 使用占位符，彻底避开 f-string 语法冲突
    prompt_template = """
    You are an AI Mentor. Analyze: '{title}'. 
    Return a STRICT JSON object with:
    "cn_title": "吸引人的中文标题",
    "en_summary": "120-word deep professional summary for audio recording",
    "cn_analysis": "300字深度解析",
    "mental_model": "对应的思维模型名称(如：第一性原理, 复利效应等)",
    "case_study": "实战案例",
    "vocab_list": [{"word": "Keyword", "meaning": "中文意思", "usage": "例句"}],
    "reflection": ["反思1", "反思2"]
    """
    prompt = prompt_template.replace("{title}", title)
    
    try:
        res = requests.post(url, 
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, 
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}},
            timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return None

async def gen_voice(text, filename):
    try:
        # Ryan 的深沉英音更适合长时间收听
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
                # 朗读 120 字长摘要，时长约 1 分钟
                asyncio.run(gen_voice(item.get('en_summary', 'Summarizing...'), audio_fn))
                item['audio_file'] = audio_fn
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
