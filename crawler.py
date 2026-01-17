import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 核心配置
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
SOURCES = [
    ("McKinsey Insights", "https://www.mckinsey.com/insights/rss"),
    ("HBR Leadership", "https://hbr.org/rss/topic/leadership"),
    ("MIT Sloan Management", "https://sloanreview.mit.edu/feed/"),
    ("Strategy+Business", "https://www.strategy-business.com/rss/all_articles"),
    ("Wharton Knowledge", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Insead Knowledge", "https://knowledge.insead.edu/rss/all"),
    ("Forbes Leadership", "https://www.forbes.com/leadership/feed/"),
    ("Fast Company Strategy", "https://www.fastcompany.com/strategy/rss"),
    ("Entrepreneur", "https://www.entrepreneur.com/topic/leadership.rss"),
    ("Inc Strategy", "https://www.inc.com/rss/strategy-and-operations")
]

# 教亮级 Prompt：设定价值阈值
PROMPT_TEMPLATE = """
Task: You are the Intelligence Engine for 'Read & Rise'. 
Content to Analyze: {title}

Strict Filter Rules:
1. If the content is PR news, generic motivation, or repetitive corporate fluff, output: {{"status": "discard"}}
2. If it contains original logic, data-backed insights, or deep leadership challenges, proceed.

Output JSON Format ONLY:
{{
    "status": "retain",
    "core_issue": "一句话总结核心议题",
    "fact_check": ["关键数据点或事实1", "事实2", "事实3"],
    "leader_value": "为什么企业 Leader 需要关注这个？(So What)",
    "golden_phrase": "一句话实战金句",
    "dimension_scores": {{"Strategic": 8, "Team": 7, "Innovation": 6, "Decision": 9, "Execution": 5}},
    "deep_tags": ["#组织演化", "#决策模型"]
}}
"""

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat", # 这里建议未来升级为 deepseek-reasoner 开启 O1 级别的逻辑
        "messages": [{"role": "system", "content": "You are an Elite Executive Coach. Output valid JSON."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def run():
    os.makedirs("data", exist_ok=True)
    articles = []
    print(f"--- 探针启动：{datetime.now()} ---")
    
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            entry = feed.entries[0]
            
            res = ask_ai(PROMPT_TEMPLATE.format(title=entry.title))
            
            if res and res.get("status") == "retain":
                res.update({
                    "id": str(uuid.uuid4())[:6],
                    "source": name,
                    "original_title": entry.title,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                articles.append(res)
                print(f"✅ 捕获硬核内容: {entry.title[:30]}...")
            else:
                print(f"🗑️ 过滤无效信息: {entry.title[:30]}...")
        except: continue

    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
