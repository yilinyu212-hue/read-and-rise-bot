import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 10 个顶级全球智库源 ---
RSS_SOURCES = [
    {"name": "HBR (领导力)", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey (行业洞察)", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist (商业频道)", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review (技术管理)", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company (创新思维)", "url": "https://www.fastcompany.com/business/rss"},
    {"name": "Fortune (财富内参)", "url": "https://fortune.com/feed/all/"},
    {"name": "Strategy+Business (战略)", "url": "https://www.strategy-business.com/rss"},
    {"name": "Wired (商业科技)", "url": "https://www.wired.com/feed/rss"},
    {"name": "Aeon (人文哲学)", "url": "https://aeon.co/feed.rss"},
    {"name": "TechCrunch (创投风向)", "url": "https://feedpress.me/techcrunch"}
]

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    prompt_tpl = """
    Analyze: '{title}'. Return STRICT JSON:
    {{
        "cn_title": "吸引领导者的中文标题",
        "en_summary": "Write a 120-word professional English summary for audio training.",
        "cn_analysis": "300字教练视角解析 (Read & Rise 逻辑)。",
        "mental_model": "对应的思维模型",
        "vocab_list": [{"word": "地道词汇", "meaning": "中文意思", "usage": "商务用法例句"}],
        "case_study": "实战应用案例",
        "reflection": ["反思建议1", "反思建议2"]
    }}"""
    prompt = prompt_tpl.replace("{title}", title)
    
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        res = requests.post(url, headers=headers, json={
            "model": "deepseek-chat", 
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return None

async def gen_voice(text, filename):
    try:
        # Ryan 是深沉且具有权威感的英音男声
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
                # 朗读 120 字摘要，时长约 1 分钟
                asyncio.run(gen_voice(item.get('en_summary', entry.title), audio_fn))
                item['audio_file'] = audio_fn
                item['source_name'] = s['name']
                all_data.append(item)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": all_data, "update_time": datetime.now().strftime("%Y-%m-%d")}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
