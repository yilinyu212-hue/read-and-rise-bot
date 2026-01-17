import os, requests, json, feedparser, uuid, time
from datetime import datetime

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

# 针对企业主的 10 个战略源
SOURCES = [
    ("HBR Leadership", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey Insights", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan Review", "https://sloanreview.mit.edu/feed/"),
    ("Wharton Knowledge", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Stanford GSB", "https://www.gsb.stanford.edu/insights/feed"),
    ("First Round Review", "https://review.firstround.com/feed.xml")
]

def push_to_notion(data):
    if not NOTION_TOKEN or not DATABASE_ID: return
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data['title']}}]},
            "Source": {"select": {"name": data['source']}},
            "Date": {"rich_text": [{"text": {"content": data['date']}}]},
            "Insight": {"rich_text": [{"text": {"content": data['coaching_brief']}}]}
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
            {"role": "system", "content": "你是一位拥有20年经验的企业教练，擅长将全球管理理论转化为国内中小企业主的实战方案。输出严格遵循 JSON。"},
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
            
            # AI 教练逻辑：抓取核心 -> 生成中英对比 -> 给出教练建议
            prompt = f"""分析文章: '{entry.title}'
            请生成以下 JSON 字段：
            1. en_title: 原文标题
            2. cn_title: 中文战略标题
            3. coaching_brief: 针对国内企业主的100字教练洞察（为何要看这个）
            4. socratic_questions: 给企业主的3道反思题
            5. action_steps: 3步落地动作
            6. dimension_scores: 5个维度(战略、团队、创新、决策、执行)的评分(1-10)
            """
            res = ask_ai(prompt)
            if res:
                res.update({"id": str(uuid.uuid4())[:6], "source": name, "date": current_date, "title": res['cn_title']})
                articles.append(res)
                push_to_notion(res) # 同步到 Notion
                print(f"✅ Coach Synced: {name}")
        except: continue

    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
