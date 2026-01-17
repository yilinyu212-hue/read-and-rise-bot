import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 环境变量 (保持不变)
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

SOURCES = [
    ("HBR", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan", "https://sloanreview.mit.edu/feed/"),
    ("Wharton", "https://knowledge.wharton.upenn.edu/feed/")
]

def push_to_notion(data):
    if not NOTION_TOKEN or not DATABASE_ID: return
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    # 将 Coaching 逻辑和语言资产存入 Notion
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data['cn_title']}}]},
            "Source": {"select": {"name": data['source']}},
            "Date": {"rich_text": [{"text": {"content": data['date']}}]},
            "Insights": {"rich_text": [{"text": {"content": f"Coaching: {data['coaching_brief']}\nLanguage: {data['lingo_asset']['vocabulary'][0]}"}}]}
        }
    }
    requests.post(url, headers=headers, json=payload)

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位拥有20年全球管理经验的企业教练，擅长萃取管理智慧与商业英语。输出严格遵循 JSON。"},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {API_KEY}"}, json=payload, timeout=60)
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
            
            # --- 增加 Lingo Asset 板块 ---
            prompt = f"""
            分析文章 '{entry.title}'。生成 JSON：
            1. cn_title: 中文战略标题, 2. en_title: 英文原题
            3. coaching_brief: 针对国内企业主的100字实战洞察
            4. socratic_questions: 3道提问
            5. lingo_asset: {{
                "vocabulary": ["核心词汇1 (中文释义)", "核心词汇2"],
                "golden_sentence": "原文中最具领导力的句子",
                "usage_tip": "这个句子在管理场景下如何使用"
            }}
            6. scores: {{'Strategic':8,'Decision':7,'Execution':9}}
            """
            res = ask_ai(prompt)
            if res:
                res.update({"source": name, "date": current_date, "id": str(uuid.uuid4())[:6]})
                articles.append(res)
                push_to_notion(res)
                print(f"✅ Intelligence Captured: {name}")
                time.sleep(1)
        except: continue

    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
