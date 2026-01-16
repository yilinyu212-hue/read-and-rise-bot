import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 配置读取
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_coach_notes(title):
    if not DEEPSEEK_KEY: return {"notes": "AI 密钥未配置", "tags": ["General"]}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    
    # 针对教练身份深度定制的专业 Prompt
    prompt = f"""
    作为一名拥有MBA背景的顶级职场英语教练，请针对文章《{title}》制作讲义。
    
    1. 首先，请从以下标签中选择1-2个最贴切的分类：[Leadership, Strategy, Management, Innovation, Career, Economy]。
    2. 然后，按以下模块输出深度解析（使用Markdown格式）：
    
    ### 🧠 [Logic & Insight / 商业逻辑洞察]
    - **Context**: 简述行业背景或管理挑战。
    - **Logic Analysis**: 拆解文章论证逻辑。
    
    ### 🗣️ [Executive Language / 领袖语言工坊]
    - **Power Words**: 3个高阶职场词汇（含音标、文中义、领袖级例句）。
    - **Golden Structure**: 1个体现商业逻辑的句式拆解。
    
    ### 🤝 [Coaching Corner / 教练锦囊]
    - **Actionable Advice**: 给管理者的实战建议。
    
    最后，请严格按以下 JSON 格式输出：
    {{"tags": ["标签1", "标签2"], "notes": "Markdown格式的内容"}}
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位专业的企业领袖培训师。"},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except:
        return json.dumps({"tags": ["General"], "notes": "解析生成中..."})

def run():
    # 扩展来源：HBR, WSJ, Economist, Fortune
    SOURCES = [
        {"name": "HBR (Leadership)", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist (Briefing)", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "WSJ (Business)", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Fortune", "url": "https://fortune.com/feed/"}
    ]
    
    all_articles = []
    print("🚀 Read & Rise 多源教研任务开始...")

    for src in SOURCES:
        feed = feedparser.parse(src['url'])
        # 每个来源取最新 1-2 篇，避免运行时间过长
        for entry in feed.entries[:1]:
            print(f"📘 研读中 [{src['name']}]: {entry.title}")
            
            raw_ai_output = get_coach_notes(entry.title)
            try:
                ai_data = json.loads(raw_ai_output)
            except:
                ai_data = {"tags": ["Business"], "notes": raw_ai_output}
            
            # 1. 同步到 Notion (包含标签属性)
            try:
                notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": entry.title}}]},
                        "Source": {"select": {"name": src['name']}},
                        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                        "Status": {"status": {"name": "To Read"}}
                    },
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": ai_data['notes'][:2000]}}]
                            }
                        }
                    ]
                )
            except Exception as e:
                print(f"❌ Notion 失败: {e}")

            # 2. 收集数据供网页调用
            all_articles.append({
                "source": src['name'],
                "title": entry.title,
                "content": ai_data['notes'],
                "tags": ai_data['tags'],
                "link": entry.link,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # 保存数据
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print("🎯 多源同步已圆满完成！")

if __name__ == "__main__":
    run()
