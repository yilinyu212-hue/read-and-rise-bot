import os, feedparser, requests, json
from datetime import datetime
from notion_client import Client

# 读取配置
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_ai_lesson_plan(title):
    if not DEEPSEEK_KEY: return "未配置 AI 秘钥"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    
    # 针对英文老师设计的专业教研 Prompt
    prompt = f"""
    作为外刊精读专家，请针对文章《{title}》制作一份【英语学习精读讲义】：
    
    1. 🇬🇧 【Original Golden Sentence / 原文金句】
       - 摘录一段最值得学习的长难句。
       - [Syntax Analysis]: 深度拆解语法结构（如倒装、虚拟语气、伴随状语等）。
    
    2. 📝 【Vocabulary Building / 词汇积累】
       - 提取3个高阶词汇，格式：单词 [音标] (词性) 含义 + 语境搭配。
    
    3. 💡 【Critical Thinking / 核心观点】
       - 中文深度解析文章的背景、逻辑与争议点。
    
    4. ✍️ 【Writing & Speaking / 句型仿写】
       - 提炼1个文中的高阶逻辑连接词或句式，并给出一个教育场景的仿写。
    
    请使用 Markdown 格式，注重英语学习的专业性。
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位拥有10年经验的顶级外刊精读教练，擅长深度语法解析与教研。"},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except:
        return "AI 解析生成中..."

def run():
    SOURCES = [
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "NYT", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"}
    ]
    
    all_articles = []
    print("🚀 Read & Rise 教研笔记生成中...")

    for src in SOURCES:
        feed = feedparser.parse(src['url'])
        for entry in feed.entries[:2]:
            print(f"正在研读: {entry.title}")
            lesson_plan = get_ai_lesson_plan(entry.title)
            
            # 1. 在 Notion 创建页面，并把笔记写入页面正文
            try:
                new_page = notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": entry.title}}]},
                        "Source": {"select": {"name": src['name']}},
                        "Link": {"url": entry.link},
                        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                        "Status": {"status": {"name": "To Read"}}
                    },
                    # 这是关键：把解析内容写入页面正文 (Blocks)
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": lesson_plan[:2000]}}] # 每一块限2000字
                            }
                        }
                    ]
                )
                print(f"✅ Notion 详情页已生成")
            except Exception as e:
                print(f"❌ Notion 失败: {e}")

            all_articles.append({
                "source": src['name'],
                "title": entry.title,
                "content": lesson_plan,
                "link": entry.link,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # 保存网站数据
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
