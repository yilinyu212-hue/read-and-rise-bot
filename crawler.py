import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")

def get_ai_coach_data(title):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""
    作为精英管理教练，请针对《{title}》制作讲义。
    必须按以下 JSON 格式返回，不要有任何多余文字：
    {{
      "tags": ["Leadership", "Strategy", "Innovation"],
      "en_excerpt": "A high-quality paragraph (50-80 words) from original.",
      "cn_translation": "该段落的专业商务中文翻译。",
      "vocabulary": "Markdown格式：3个高阶词汇解析。",
      "insight": "Markdown格式：对管理者的3点洞察。",
      "action": "实战建议。"
    }}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a professional business coach."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return "{}"

def run():
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Fortune", "url": "https://fortune.com/feed/"},
        {"name": "FT", "url": "https://www.ft.com/?format=rss"},
        {"name": "Forbes", "url": "https://www.forbes.com/innovation/feed/"},
        {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"},
        {"name": "Atlantic", "url": "https://www.theatlantic.com/feed/all/"}
    ]
    
    results = []
    for src in SOURCES:
        try:
            feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": "Mozilla/5.0"}, timeout=15).content)
            if feed.entries:
                entry = feed.entries[0]
                ai_json = json.loads(get_ai_coach_data(entry.title))
                results.append({
                    "source": src['name'], "title": entry.title,
                    "en_text": ai_json.get('en_excerpt', ''),
                    "cn_text": ai_json.get('cn_translation', ''),
                    "tags": ai_json.get('tags', []),
                    "vocabulary": ai_json.get('vocabulary', ''),
                    "insight": ai_json.get('insight', ''),
                    "action": ai_json.get('action', ''),
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
        except: continue

    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
