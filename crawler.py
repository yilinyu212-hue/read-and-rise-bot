import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime
import time

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

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
    Analyze article: '{title}'. Return STRICT JSON:
    {{
        "cn_title": "中文标题",
        "en_summary": "120-word professional English summary for audio training.",
        "cn_analysis": "300字深度解析",
        "mental_model": "核心思维模型名称",
        "case_study": "实战管理/教学案例",
        "vocab_list": [
            {{"word": "Term", "meaning": "意思", "usage": "商务用法例句"}}
        ],
        "reflection": ["反思建议1", "反思建议2"]
    }}
    """
    prompt = prompt_tpl.replace("{title}", title)
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        res = requests.post(url, headers=headers, json={
            "model": "deepseek-chat", 
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return None

async def gen_voice(text, filename):
    try:
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
        await communicate.save(filename)
    except: pass

def main():
    new_items = []
    print(f"Starting crawl at {datetime.now()}...")
    
    for i, s in enumerate(RSS_SOURCES):
        feed = feedparser.parse(s['url'])
        if feed.entries:
            entry = feed.entries[0]
            print(f"Processing source {i+1}/10: {s['name']}")
            content = ai_analyze(entry.title)
            if content:
                item = json.loads(content)
                item['date'] = datetime.now().strftime("%Y-%m-%d")
                item['source_name'] = s['name']
                audio_fn = f"audio_{i}.mp3"
                # 生成长音频
                asyncio.run(gen_voice(item.get('en_summary', ''), audio_fn))
                item['audio_file'] = audio_fn
                new_items.append(item)
            time.sleep(1) # 频率限制保护

    # 归档至知识库 (Knowledge Base Archive)
    history_file = "knowledge_base.json"
    history_data = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            try: history_data = json.load(f)
            except: history_data = []
    
    # 追加新内容到历史库开头
    existing_titles = [x.get('cn_title') for x in history_data]
    for item in new_items:
        if item['cn_title'] not in existing_titles:
            history_data.insert(0, item)
    
    # 保存结果
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": new_items}, f, ensure_ascii=False)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
