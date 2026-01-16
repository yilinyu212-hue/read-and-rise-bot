import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 配置读取
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_ai_deep_notes(title):
    if not DEEPSEEK_KEY: return "AI 密钥未配置"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    
    # 更加深度、专业的教研 Prompt
    prompt = f"""
    作为外刊精读专家，请针对《{title}》制作一份深度教研笔记：
    
    1. 💡【核心纵览】：用3行以内文字解析文章的社会背景与核心争议点。
    2. 📝【精读笔记】：
       - 逻辑拆解：简述文章是如何展开论述的（Start -> Develop -> End）。
       - 深度见解：挖掘文中一个容易被忽视的细节或深度含义。
    3. 🎯【地道表达】：
       - 提取2个高阶词组（含搭配、中英文对照及例句）。
       - 提取1个长难句，进行语法结构拆解（如定语从句、倒装等）。
    4. ✍️【写作/口语借鉴】：
       - 提炼一个文中的逻辑衔接句式。
       - 针对“教育策展”或“教学场景”提供一个仿写例句。
    
    要求：逻辑严密，语言专业且富有启发性，使用 Markdown 格式排版。
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位拥有10年经验的顶级外刊精读教练，擅长深度逻辑分析和语言点挖掘。"},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"笔记生成中，暂遇小问题: {e}"

def run():
    SOURCES = [
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "NYT", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"}
    ]
    
    all_articles = []
    print("🚀 开始生成深度精读笔记...")
    
    for src in SOURCES:
        feed = feedparser.parse(src['url'])
        for entry in feed.entries[:2]:
            print(f"📘 正在研读: {entry.title}")
            notes = get_ai_deep_notes(entry.title)
            
            # 同步到 Notion
            try:
                notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": entry.title}}]},
                        "Source": {"select": {"name": src['name']}},
                        "Link": {"url": entry.link},
                        "AI Summary": {"rich_text": [{"text": {"content": notes[:1950]}}]}, # Notion 单元格上限约2000字符
                        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                        "Status": {"status": {"name": "To Read"}}
                    }
                )
            except Exception as e:
                print(f"❌ Notion 同步失败: {e}")

            all_articles.append({
                "source": src['name'],
                "title": entry.title,
                "content": notes, # 网站端显示完整的笔记
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # 更新本地数据
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
