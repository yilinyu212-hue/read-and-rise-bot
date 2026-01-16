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
    
    # 强化英文段落和句式拆解的 Prompt
    prompt = f"""
    作为精英英语教练，请针对《{title}》制作讲义。
    
    请严格按以下结构输出 Markdown：
    1. [Tags]: 从 Leadership, Strategy, Tech, Career 中选2个。
    2. [Reading Excerpt / 原文精选]: 摘录文中一段最能代表核心观点的【英文原文】（约50-100词）。
    3. [Vocabulary]: 3个职场高阶词汇（含音标、双语释义）。
    4. [Sentence Lab / 句法实验室]: 选一个高阶句式，进行 [Structure Analysis] 和 [Coach's Imitation / 教练仿写]。
    5. [Insight]: 深度逻辑解析。
    
    最后请输出 JSON：{{"tags": ["标签"], "excerpt": "英文原文", "notes": "Markdown笔记"}}
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a professional business English coach."},
                     {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except:
        return json.dumps({"tags": ["General"], "excerpt": "", "notes": "AI is thinking..."})

def run():
    # 优化后的 Headers 防止被 HBR 等屏蔽
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"}
    ]
    
    all_articles = []
    for src in SOURCES:
        try:
            # 使用 requests 先抓取 xml，避开简单爬虫过滤
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=20)
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:1]:
                print(f"研读中: {entry.title}")
                ai_res = json.loads(get_coach_notes(entry.title))
                
                # 同步 Notion (略)
                
                all_articles.append({
                    "source": src['name'],
                    "title": entry.title,
                    "excerpt": ai_res.get('excerpt', ''),
                    "content": ai_res.get('notes', ''),
                    "tags": ai_res.get('tags', []),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "img": "https://images.unsplash.com/photo-1454165833767-0266b196773b?w=800" # 预留占位图
                })
        except Exception as e:
            print(f"Error fetching {src['name']}: {e}")

    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
