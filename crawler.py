import requests, feedparser, json, os, asyncio, edge_tts
from datetime import datetime

# 环境变量读取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 扩充全球智库源
RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fortune", "url": "https://fortune.com/feed/all/"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    
    # 核心提示词：中英双语输出 + 修正大括号转义
    prompt = f"""Analyze the business article: '{title}'. 
    You must return a strict JSON object with these keys:
    {{
        "en_summary": "A 150-word professional English summary.",
        "cn_analysis": "300字中文深度决策价值分析，面向企业主。",
        "actions": ["Action Point 1", "Action Point 2"],
        "model_scores": {{"Strategy": 90, "Innovation": 85, "Execution": 75}}
    }}"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", 
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except Exception as e:
        print(f"Error analyzing {title}: {e}")
        return None

async def generate_audio(text):
    # 使用 RyanNeural (BBC 风格伦敦腔)
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save("daily_briefing.mp3")

def run_sync():
    print("🚀 Read & Rise 数据工厂启动...")
    
    # 初始化/加载旧数据
    books = []
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                books = json.load(f).get("books", [])
        except: pass

    data = {"briefs": [], "books": books, "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    # 抓取并分析每源第一条
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
                print(f"✅ 已抓取: {s['name']}")
    
    # 合成播报音频
    if data["briefs"]:
        titles = " and ".join([b['title'][:50] for b in data['briefs'][:3]])
        script = f"Hi Leaders! Today's Read and Rise briefing features insights from {titles}. Let's explore the strategic value together."
        asyncio.run(generate_audio(script))
        print("🎙️ 语音播报合成成功")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("🏁 全部同步任务完成")

if __name__ == "__main__":
    run_sync()
