import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 配置读取
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_coach_notes(title):
    if not DEEPSEEK_KEY: return "AI 密钥未配置"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    
    # 针对“英语培训师 + 管理教练”身份深度定制的 Prompt
    prompt = f"""
    你是一位拥有MBA背景的顶级职场英语教练。请针对文章《{title}》制作一份【管理精英精读讲义】。
    
    内容必须严格按以下四个模块输出：
    
    ### 🧠 [Logic & Insight / 商业逻辑洞察]
    - **Context**: 用两句话说明这篇文章探讨的行业背景或管理挑战。
    - **Logic Analysis**: 拆解文章的论证逻辑（如：现状-痛点-对策）。
    
    ### 🗣️ [Executive Language / 领袖语言工坊]
    - **Power Words**: 提取3个高阶职场词汇，给出 [音标]、[文中含义] 及 [董事会级别例句]。
    - **Golden Structure**: 摘录原文中1个体现商业逻辑的句式，并进行语法解析。
    
    ### 🤝 [Coaching Corner / 教练锦囊]
    - **Actionable Advice**: 作为一个管理教练，你会建议学员如何将文中的观点应用到团队管理或个人职业规划中？
    
    ### ✍️ [Scenario Simulation / 场景仿写]
    - 提供一个基于文中高阶句式的“职场汇报”或“商务邮件”场景的仿写。
    
    要求：专业、干练，英语术语与中文解析交替，排版使用清晰的 Markdown 格式。
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位专注于企业领袖培训的资深英语教练。"},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"笔记生成中，暂遇故障: {e}"

def run():
    SOURCES = [
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "NYT", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"}
    ]
    
    all_articles = []
    print("🚀 Read & Rise 教案库更新中...")

    for src in SOURCES:
        feed = feedparser.parse(src['url'])
        for entry in feed.entries[:2]:
            print(f"📘 研读中: {entry.title}")
            coach_notes = get_coach_notes(entry.title)
            
            # 同步到 Notion (包含正文写入)
            try:
                notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": entry.title}}]},
                        "Source": {"select": {"name": src['name']}},
                        "Link": {"url": entry.link},
                        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                        "Status": {"status": {"name": "To Read"}}
                    },
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": coach_notes[:2000]}}]
                            }
                        }
                    ]
                )
            except Exception as e:
                print(f"❌ Notion 写入失败: {e}")

            all_articles.append({
                "source": src['name'],
                "title": entry.title,
                "content": coach_notes,
                "link": entry.link,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # 保存至 GitHub 供网页调用
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print("🎯 教研同步完成！")

if __name__ == "__main__":
    run()
