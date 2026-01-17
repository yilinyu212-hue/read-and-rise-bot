import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 获取环境变量
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

SOURCES = [
    ("HBR Leadership", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey Insights", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan Review", "https://sloanreview.mit.edu/feed/"),
    ("Strategy+Business", "https://www.strategy-business.com/rss/all_articles"),
    ("Knowledge at Wharton", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Insead Knowledge", "https://knowledge.insead.edu/rss/all"),
    ("First Round Review", "https://review.firstround.com/feed.xml")
]

def push_to_notion(data):
    if not NOTION_TOKEN or not DATABASE_ID: return
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data['title']}}]},
            "Source": {"select": {"name": data['source']}},
            "Date": {"rich_text": [{"text": {"content": data['date']}}]},
            "Insight": {"rich_text": [{"text": {"content": data.get('speaking_gold', 'Strategic Insight')}}]}
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a Senior Executive Coach. Output JSON."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def run():
    os.makedirs("data", exist_ok=True)
    articles = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            entry = feed.entries[0]
            
            prompt = f"Analyze: '{entry.title}'. Output JSON: perspectives(ceo_view, org_psychology, defense_view), socratic_questions(list), dimension_scores(dict), speaking_gold(str)."
            res = ask_ai(prompt)
            if res:
                res.update({"id": str(uuid.uuid4())[:6], "title": entry.title, "source": name, "date": current_date})
                articles.append(res)
                push_to_notion(res) # 核心同步
                print(f"✅ Synced: {name}")
        except: continue

    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
