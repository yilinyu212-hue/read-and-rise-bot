import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 配置
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_coach_notes(title):
    if not DEEPSEEK_KEY: return {"tags": ["General"], "notes": "Key missing"}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    
    prompt = f"""
    作为精英英语教练，请针对《{title}》制作讲义。
    请输出 JSON 格式，包含以下字段：
    1. [tags]: 2个分类标签。
    2. [excerpt]: 摘录50词左右的英文原文。
    3. [notes]: 包含 Vocabulary, Sentence Lab(含语法拆解和仿写), Insight 的 Markdown 笔记。
    4. [image_prompt]: 请根据文章主题，写一段用于生成商业插画的英文描述词（Prompt）。
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a professional business coach."},
                     {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except:
        return json.dumps({"tags": ["General"], "notes": "AI is thinking...", "image_prompt": "Business strategy concept"})

def run():
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"}
    ]
    
    all_articles = []
    for src in SOURCES:
        try:
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=20)
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:1]:
                ai_data = json.loads(get_coach_notes(entry.title))
                
                # 使用关键词从 Unsplash 自动获取高度相关的图片（无需秘钥，完全免费且合法）
                img_url = f"https://source.unsplash.com/800x450/?{ai_data.get('image_prompt', 'business').replace(' ', ',')}"
                
                all_articles.append({
                    "source": src['name'],
                    "title": entry.title,
                    "excerpt": ai_data.get('excerpt', ''),
                    "content": ai_data.get('notes', ''),
                    "tags": ai_data.get('tags', []),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "img": img_url # 动态生成的图片地址
                })
        except Exception as e: print(f"Error: {e}")

    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
