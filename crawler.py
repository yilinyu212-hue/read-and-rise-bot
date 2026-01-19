import requests, feedparser, json, os, random
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"}
]

def ai_analyze(title, link):
    if not DEEPSEEK_API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""作为顶级商业顾问解析文章: "{title}"。
    必须返回 JSON 格式，包含：
    1. cn_summary: 3条最利于决策的中文摘要
    2. en_summary: 3条英文核心点
    3. case_study: 文章中的商业实战案例解析
    4. reflection_flow: 3个针对管理者的深度提问
    5. vocab_bank: 3个高阶商业词汇(含例句)
    6. model_scores: 对该文的“战略、创新、洞察、组织、执行”五个维度打分(0-100)
    """
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": 0.3
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except: return None

def run_sync():
    # 保留旧书数据
    books = []
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                books = json.load(f).get("books", [])
        except: pass

    data = {
        "briefs": [], 
        "books": books, 
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    for s in RSS_SOURCES:
        feed = feedparser.parse(s['url'])
        if feed.entries:
            res = ai_analyze(feed.entries[0].title, feed.entries[0].link)
            if res:
                res["source"] = s['name']
                data["briefs"].append(res)
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
