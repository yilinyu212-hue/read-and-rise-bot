import os, feedparser, requests, json
from datetime import datetime

# --- 配置区 ---
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
# 模拟真实浏览器，防止被 HBR/FT 等屏蔽
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# --- 核心 AI 解析函数 (文章版) ---
def get_ai_article_data(title):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""
    作为顶级英语培训师与管理教练，请针对《{title}》制作深度讲义。
    必须按以下 JSON 格式返回，不要有任何多余解释：
    {{
      "level": "Advanced (C1)",  // 选项: Intermediate (B2), Advanced (C1), Expert (C2)
      "tags": ["Leadership", "Strategy"],
      "en_excerpt": "挑选文中包含高级表达的核心段落(60-100字)。",
      "cn_translation": "该段落的商务专家级中文翻译。",
      "vocabulary_pro": "Markdown格式：3个词汇及其商务应用场景。",
      "syntax_analysis": "Markdown格式：对文中的高阶句法进行拆解。",
      "output_playbook": {{
          "speaking": "会议/演讲中如何引用此观点的模板。",
          "writing": "周报/邮件中可套用的高阶句型。"
      }},
      "insight": "对管理者的3点洞察。"
    }}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a senior Business English pedagogical expert."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return {}

# --- 核心 AI 解析函数 (书籍版) ---
def get_book_insight(book_name, author):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""
    作为管理教练，请为书籍《{book_name}》（作者：{author}）制作教案。
    按以下 JSON 格式返回：
    {{
      "intro": "核心价值简介 (中英双语)。",
      "takeaways": ["重点1(含英语关键词)", "重点2", "重点3"],
      "why_read": "推荐理由：为什么管理者必须读这本书？",
      "image_query": "一到两个关键词用于搜索封面背景"
    }}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a professional business librarian."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return {"intro": "N/A", "takeaways": [], "why_read": "N/A"}

# --- 主运行流程 ---
def run():
    # 1. 文章抓取配置 (8大来源)
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Fortune", "url": "https://fortune.com/feed/"},
        {"name": "FT", "url": "https://www.ft.com/?format=rss"},
        {"name": "Forbes", "url": "https://www.forbes.com/innovation/feed/"},
        {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"},
        {"name": "Atlantic", "url": "https://www.theatlantic.com/feed/all/"}
    ]
    
    # 2. 书籍推荐配置 (您可以在这里随时增减书单)
    BOOK_LIST = [
        {"title": "The Pyramid Principle", "author": "Barbara Minto", "tag": "Logic"},
        {"title": "High Output Management", "author": "Andrew Grove", "tag": "Leadership"},
        {"title": "Atomic Habits", "author": "James Clear", "tag": "Behavior"}
    ]

    os.makedirs('data', exist_ok=True)

    # --- 执行文章抓取 ---
    all_articles = []
    print("🚀 开始抓取外刊精读...")
    for src in SOURCES:
        try:
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=15)
            feed = feedparser.parse(resp.content)
            if feed.entries:
                entry = feed.entries[0]
                print(f"📖 研读文章: {entry.title}")
                ai_data = get_ai_article_data(entry.title)
                if ai_data:
                    all_articles.append({
                        "source": src['name'], "title": entry.title,
                        "level": ai_data.get('level', 'C1'),
                        "en_text": ai_data.get('en_excerpt', ''),
                        "cn_text": ai_data.get('cn_translation', ''),
                        "tags": ai_data.get('tags', []),
                        "vocabulary": ai_data.get('vocabulary_pro', ''),
                        "syntax": ai_data.get('syntax_analysis', ''),
                        "playbook": ai_data.get('output_playbook', {}),
                        "insight": ai_data.get('insight', ''),
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
        except Exception as e: print(f"❌ {src['name']} 失败: {e}")

    # --- 执行书籍解析 ---
    all_books = []
    print("📚 开始生成书籍教案...")
    for b in BOOK_LIST:
        try:
            print(f"📘 研读名著: {b['title']}")
            insight = get_book_insight(b['title'], b['author'])
            img_url = f"https://source.unsplash.com/800x600/?{insight.get('image_query', 'business,book')}"
            all_books.append({
                "title": b['title'], "author": b['author'], "tag": b['tag'],
                "img": img_url, **insight
            })
        except Exception as e: print(f"❌ 书籍 {b['title']} 失败: {e}")

    # --- 统一保存数据 ---
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open('data/books.json', 'w', encoding='utf-8') as f:
        json.dump(all_books, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 全部更新完成！文章:{len(all_articles)} 篇, 书籍:{len(all_books)} 本。")

if __name__ == "__main__":
    run()
