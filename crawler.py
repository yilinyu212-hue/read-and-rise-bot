import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 环境变量
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

# 10个核心信源
SOURCES = [
    ("HBR", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan", "https://sloanreview.mit.edu/feed/"),
    ("Wharton", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Stanford GSB", "https://www.gsb.stanford.edu/insights/feed"),
    ("First Round", "https://review.firstround.com/feed.xml"),
    ("Strategy+Business", "https://www.strategy-business.com/rss/all_articles"),
    ("Insead", "https://knowledge.insead.edu/rss/all"),
    ("LSE Business", "https://blogs.lse.ac.uk/businessreview/feed/"),
    ("Gartner", "https://www.gartner.com/en/newsroom/rss-feeds")
]

def push_to_notion(data):
    if not NOTION_TOKEN or not DATABASE_ID:
        print("⚠️ 警告: 缺少 Notion 配置")
        return
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 严格对应你截图中的表头名
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data['cn_title']}}]},
            "Source": {"select": {"name": data['source']}},
            "Date": {"rich_text": [{"text": {"content": data['date']}}]},
            "Coach_Insight": {"rich_text": [{"text": {"content": data['coaching_brief']}}]},
            "Original_Title": {"rich_text": [{"text": {"content": data['en_title']}}]},
            "Socratic_Questions": {"rich_text": [{"text": {"content": "\n".join(data['socratic_questions'])}}]},
            "Lingo_Asset": {"rich_text": [{"text": {"content": f"Golden Sentence: {data['lingo_asset']['golden_sentence']}"}}]},
            "Case_Scenario": {"rich_text": [{"text": {"content": data['case_lab']['scenario']}}]},
            "Leader_Reflection": {"rich_text": [{"text": {"content": "Waiting for feedback..."}}]}
        }
    }
    
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        print(f"✅ Notion 同步成功: {data['cn_title']}")
    else:
        print(f"❌ Notion 同步失败: {res.status_code} - {res.text}")

def ask_ai(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位顶级企业教练。输出严格遵循JSON。"},
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
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            entry = feed.entries[0]
            
            prompt = f"分析文章 '{entry.title}'。生成JSON: cn_title, en_title, coaching_brief, socratic_questions(list), lingo_asset(dict: golden_sentence, usage_tip), case_lab(dict: scenario)."
            res = ask_ai(prompt)
            if res:
                res.update({"source": name, "date": current_date, "id": str(uuid.uuid4())[:6]})
                articles.append(res)
                push_to_notion(res) # 推送 Notion
                time.sleep(1)
        except Exception as e:
            print(f"⚠️ {name} 处理出错: {e}")

    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
