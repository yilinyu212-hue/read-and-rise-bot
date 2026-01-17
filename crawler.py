import os, requests, json, feedparser, uuid, time
from datetime import datetime

# 环境变量
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

# 筛选出的顶级信源
SOURCES = [
    ("HBR", "https://hbr.org/rss/topic/leadership"),
    ("McKinsey", "https://www.mckinsey.com/insights/rss"),
    ("MIT Sloan", "https://sloanreview.mit.edu/feed/"),
    ("Wharton", "https://knowledge.wharton.upenn.edu/feed/"),
    ("Stanford GSB", "https://www.gsb.stanford.edu/insights/feed")
]

def push_to_notion(data):
    """将萃取的案例和语言资产同步到 Notion"""
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
            "Name": {"title": [{"text": {"content": data['cn_title']}}]},
            "Type": {"select": {"name": "Case Study"}},
            "Source": {"select": {"name": data['source']}},
            "English_Title": {"rich_text": [{"text": {"content": data['en_title']}}]},
            "Lingo_Asset": {"rich_text": [{"text": {"content": data['lingo_asset']['golden_sentence']}}]},
            "Date": {"rich_text": [{"text": {"content": data['date']}}]}
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
            {"role": "system", "content": "你是一位拥有全球视野的企业教练，擅长将商业外刊转化为高管案例库和语言学习资产。输出严格遵循 JSON。"},
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
            
            # --- 核心：Prompt 调整，侧重案例萃取和语言资产 ---
            prompt = f"""
            分析文章: '{entry.title}'
            请以企业教练的视角生成以下 JSON 结构：
            1. cn_title: 中文实战标题
            2. en_title: 英文原题
            3. coaching_brief: 100字教练洞察（说明对国内企业主的实战意义）
            4. socratic_questions: [3道深度引导提问]
            5. lingo_asset: {{
                "vocabulary": ["核心词1 (释义)", "核心词2"],
                "golden_sentence": "原文中最具领导力表现力的句子",
                "usage_tip": "此句在管理场景中的应用建议"
            }}
            6. case_lab: {{
                "scenario": "将此文章背景抽象为一个50-100字的决策挑战场景",
                "key_dilemma": "核心矛盾是什么？"
            }}
            7. dimension_scores: {{"Strategic": 8, "Decision": 7, "Innovation": 6, "Execution": 7, "Team": 8}}
            """
            
            res = ask_ai(prompt)
            if res:
                res.update({
                    "id": str(uuid.uuid4())[:6], 
                    "source": name, 
                    "date": current_date
                })
                articles.append(res)
                # 同步到 Notion（作为 Hi Leaders AI 的数据库）
                push_to_notion(res)
                print(f"✅ 案例已沉淀: {name}")
                time.sleep(1) # 频率限制
        except Exception as e:
            print(f"❌ 抓取失败 {name}: {e}")

    # 保存为本地 JSON，供 Streamlit 渲染“瞭望塔”
    with open("data/library.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
