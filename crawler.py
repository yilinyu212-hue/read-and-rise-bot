import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 环境变量获取
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

# 10 个顶级信源
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
    """推送数据到 Notion，严格匹配你刚修改的字段名"""
    if not NOTION_TOKEN or not DATABASE_ID:
        print("❌ 错误：缺少 NOTION_TOKEN 或 DATABASE_ID")
        return
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data['cn_title']}}]},
            "Original_Title": {"rich_text": [{"text": {"content": data['en_title']}}]},
            "Source": {"select": {"name": data['source']}},
            "Date": {"rich_text": [{"text": {"content": data['date']}}]},
            "Coach_Insight": {"rich_text": [{"text": {"content": data['coaching_brief']}}]},
            "Socratic_Questions": {"rich_text": [{"text": {"content": "\n".join(data.get('socratic_questions', []))}}]},
            "Lingo_Asset": {"rich_text": [{"text": {"content": f"Golden Sentence: {data['lingo_asset']['golden_sentence']}\nUsage: {data['lingo_asset']['usage_tip']}"}}]},
            "Case_Scenario": {"rich_text": [{"text": {"content": data['case_lab']['scenario']}}]}
        }
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            print(f"✅ Notion 同步成功: {data['cn_title']}")
        else:
            print(f"❌ Notion 同步失败: 状态码 {res.status_code}, 原因: {res.text}")
    except Exception as e:
        print(f"❌ Notion 异常: {e}")

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位顶级企业教练和战略顾问。输出严格遵循 JSON。"},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except:
        return None

def run():
    os.makedirs("data", exist_ok=True)
    articles = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"🚀 开始执行 Read & Rise 瞭望塔同步: {current_date}")
    
    for name, url in SOURCES:
        try:
            print(f"🔍 正在检查信源: {name}...")
            feed = feedparser.parse(url)
            if not feed.entries:
                print(f"⚠️ {name} 暂时没有更新内容")
                continue
            
            entry = feed.entries[0]
            
            prompt = f"""
            分析文章 '{entry.title}'。生成 JSON：
            1. cn_title: 中文实战标题
            2. en_title: 英文标题
            3. coaching_brief: 针对国内企业主的实战洞察
            4. socratic_questions: [3道深度引导提问]
            5. lingo_asset: {{"golden_sentence": "原文金句", "usage_tip": "场景用法"}}
            6. case_lab: {{"scenario": "抽象案例场景"}}
            7. dimension_scores: {{"Strategic": 8, "Decision": 7, "Team": 9, "Innovation": 6, "Execution": 7}}
            """
            
            res = ask_ai(prompt)
            if res:
                res.update({"source": name, "date": current_date, "id": str(uuid.uuid4())[:6]})
                articles.append(res)
                # 推送 Notion
                push_to_notion(res)
                print(f"✨ {name} 处理完成")
                time.sleep(2) # 稍微延长间隔，确保 10 个源推送稳定
        except Exception as e:
            print(f"❌ 处理 {name} 时发生错误: {e}")

    # 保存本地 library.json
    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"🏁 同步结束，本地库已更新，共抓取 {len(articles)} 条案例。")

if __name__ == "__main__":
    run()
