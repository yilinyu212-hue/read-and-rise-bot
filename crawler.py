import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

# 从系统变量获取 API KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 10个顶级外刊信源
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
    if not DEEPSEEK_API_KEY:
        print("Error: DEEPSEEK_API_KEY not found.")
        return None
        
    url = "https://api.deepseek.com/chat/completions"
    
    # 核心：使用双大括号 {{ }} 避免 f-string 解析 JSON 冲突
    prompt = f"""
    As a professional mentor for educators, analyze the article title: '{title}'.
    Provide a high-level strategic briefing.
    
    Return a STRICT JSON object with these exact keys:
    {{
        "cn_title": "中文标题",
        "en_title": "{title}",
        "cn_analysis": "300字左右的中文深度摘要，强调对教育者的启发。",
        "case_study": "针对教育机构或管理者的实际应用案例拆解。",
        "mental_model": "关联的一个管理学或认知思维模型",
        "reflection_flow": ["反思问题1: ...", "反思问题2: ..."],
        "vocab_cards": [
            {{"word": "Key Term", "meaning": "中文含义"}}
        ]
    }}
    """
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.7
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI Analysis Failed for {title}: {e}")
        return None

async def generate_audio(text, filename):
    """为英文摘要生成英音播报"""
    try:
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
        await communicate.save(filename)
    except Exception as e:
        print(f"Audio Generation Failed: {e}")

def run_pipeline():
    all_items = []
    print(f"🚀 Starting update: {datetime.now()}")
    
    for i, source in enumerate(RSS_SOURCES):
        print(f"🔍 Fetching from: {source['name']}...")
        feed = feedparser.parse(source['url'])
        
        if feed.entries:
            # 只取每个源最新的第一篇文章
            top_entry = feed.entries[0]
            print(f"📝 Analyzing: {top_entry.title}")
            
            # 1. AI 分析
            ai_json_str = ai_analyze(top_entry.title)
            if ai_json_str:
                item = json.loads(ai_json_str)
                item['source'] = source['name']
                
                # 2. 生成语音文件
                audio_filename = f"audio_{i}.mp3"
                asyncio.run(generate_audio(top_entry.title, audio_filename))
                item['audio_file'] = audio_filename
                
                all_items.append(item)
    
    # 3. 保存最终结果
    final_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": all_items
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Successfully updated {len(all_items)} articles.")

if __name__ == "__main__":
    run_pipeline()
