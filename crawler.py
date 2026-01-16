import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")

def get_coach_notes(title):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""
    作为精英管理教练，请针对《{title}》制作讲义。
    请按以下 JSON 结构输出：
    {{
      "tags": ["Leadership", "Strategy", "Tech", "Career", "Economy"], 
      "en_excerpt": "原文核心段落 (50-80 words).",
      "cn_translation": "该段落的高级商务中文翻译。",
      "vocabulary": "词汇解析：3个高阶职场词汇及其在地道商业场景的应用。",
      "insight": "教练洞察：分析本文对管理者的启示或对行业的预判...",
      "action_task": "实战作业：建议的一项针对性管理行动或表达练习..."
    }}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a world-class business English coach."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except:
        return json.dumps({"tags":["General"], "en_excerpt":"N/A", "cn_translation":"N/A", "vocabulary":"N/A", "insight":"N/A", "action_task":"N/A"})

def run():
    # --- 扩充后的 8 大核心信源 ---
    SOURCES = [
        {"name": "HBR (Leadership)", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist (Briefing)", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "WSJ (Business)", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Financial Times", "url": "https://www.ft.com/?format=rss"},
        {"name": "Fortune (Leadership)", "url": "https://fortune.com/category/leadership/feed/"},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
        {"name": "The Atlantic", "url": "https://www.theatlantic.com/feed/all/"},
        {"name": "Forbes (Innovation)", "url": "https://www.forbes.com/innovation/feed/"}
    ]
    
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    all_articles = []

    for src in SOURCES:
        try:
            print(f"🌐 正在获取: {src['name']}")
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=20)
            feed = feedparser.parse(resp.content)
            
            # 每个源取最新 1 篇，确保 8 篇内容各不相同，且降低处理时间
            if feed.entries:
                entry = feed.entries[0]
                print(f"📖 正在研读: {entry.title}")
                
                ai_data = json.loads(get_coach_notes(entry.title))
                all_articles.append({
                    "source": src['name'],
                    "title": entry.title,
                    "en_text": ai_data['en_excerpt'],
                    "cn_text": ai_data['cn_translation'],
                    "tags": ai_data['tags'],
                    "vocabulary": ai_data['vocabulary'],
                    "insight": ai_data['insight'],
                    "action": ai_data['action_task'],
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "link": entry.link
                })
        except Exception as e:
            print(f"❌ {src['name']} 获取失败: {e}")

    # 保存数据
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print(f"✅ 教研库更新完成，共计 {len(all_articles)} 篇深度教案。")

if __name__ == "__main__":
    run()
