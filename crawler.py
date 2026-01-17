import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 凭证获取
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

# 完善后的 10 个顶级源
SOURCES = [
    ("HBR Leadership", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey Insights", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan Review", "https://sloanreview.mit.edu/feed/"),
    ("Strategy+Business", "https://www.strategy-business.com/rss/all_articles"),
    ("Wharton Knowledge", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Insead Knowledge", "https://knowledge.insead.edu/rss/all"),
    ("LSE Business Review", "https://blogs.lse.ac.uk/businessreview/feed/"),
    ("First Round Review", "https://review.firstround.com/feed.xml"),
    ("Stanford GSB", "https://www.gsb.stanford.edu/insights/feed"),
    ("Gartner Insights", "https://www.gartner.com/en/newsroom/rss-feeds")
]

def push_to_notion(data):
    """同步至 Notion 数字化教练库"""
    if not NOTION_TOKEN or not DATABASE_ID:
        return
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    # 请确保 Notion 数据库中有这些字段：Name (Title), Source (Select/Text), Date (Text), Insight (Text)
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data['title']}}]},
            "Source": {"select": {"name": data['source']}},
            "Date": {"rich_text": [{"text": {"content": data['date']}}]},
            "Insight": {"rich_text": [{"text": {"content": data['speaking_gold']}}]}
        }
    }
    requests.post(url, headers=headers, json=payload)

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a Senior Executive Coach. Output strictly in JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def run():
    os.makedirs("data", exist_ok=True)
    articles = []
    
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            entry = feed.entries[0]
            
            prompt = f"""Analyze: '{entry.title}'
            Role: Executive Thought Partner.
            Output JSON with:
            1. perspectives (ceo_view, org_psychology, defense_view)
            2. 3 socratic_questions
            3. dimension_scores (Strategic, Team, Innovation, Decision, Execution)
            4. challenge (scenario, options, correct_idx, coach_feedback)
            5. speaking_gold (One powerful sentence)
            """
            
            res = ask_ai(prompt)
            if res:
                res.update({
                    "id": str(uuid.uuid4())[:6], 
                    "title": entry.title, 
                    "source": name,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                articles.append(res)
                push_to_notion(res) # 推送到 Notion
                print(f"✅ Synced: {name}")
                time.sleep(1) 
        except Exception as e:
            print(f"❌ Failed {name}: {e}")

    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
