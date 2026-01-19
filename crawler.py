import requests, feedparser, json, os, random
from datetime import datetime

# 环境变量
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # 用于 TTS 语音合成

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"作为顶级商业顾问解析文章: '{title}'。返回 JSON，包含 cn_summary(3条), case_study, reflection_flow(3条), vocab_bank(3个), model_scores(战略/创新/洞察/组织/执行 0-100)。"
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": 0.3
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except: return None

# 🎙️ 新增：生成 BBC 风格播报稿并转为音频
def generate_audio_briefing(briefs):
    if not briefs or not OPENAI_API_KEY: return
    
    # 1. 生成稿件
    titles = " | ".join([b['title'] for b in briefs[:3]])
    script_prompt = f"根据今日头条：{titles}，写一段 300 字 BBC 风格播报稿。开头：'Hi, Leaders! This is your Read and Rise daily briefing...'，侧重于给高管的决策建议。"
    
    try:
        # 调用 DeepSeek 生成稿件
        res = requests.post("https://api.deepseek.com/chat/completions", headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": script_prompt}]
        })
        script = res.json()['choices'][0]['message']['content']

        # 2. 调用 OpenAI TTS 生成音频
        audio_res = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": "tts-1", "voice": "onyx", "input": script}
        )
        with open("daily_briefing.mp3", "wb") as f:
            f.write(audio_res.content)
        print("✅ 音频播报生成成功")
    except Exception as e:
        print(f"❌ 音频生成失败: {e}")

def run_sync():
    books = []
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                books = json.load(f).get("books", [])
        except: pass

    data = {"briefs": [], "books": books, "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
    
    # 执行音频生成
    generate_audio_briefing(data["briefs"])
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
