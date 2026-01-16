import os, feedparser, requests, json
from datetime import datetime

# --- 配置区 ---
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# 1. 文章解析函数 (教研讲义级别)
def get_ai_article_data(title):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""
    作为顶级英语培训师与管理教练，请针对《{title}》制作讲义。
    必须严格按以下 JSON 结构输出：
    {{
      "level": "Advanced (C1)", 
      "tags": ["Leadership", "Strategy"],
      "en_excerpt": "挑选文中60-100字包含高阶句法的核心段落。",
      "cn_translation": "专家级中文翻译。",
      "vocabulary_pro": "Markdown格式：3个高阶词汇及职场应用。",
      "syntax_analysis": "Markdown格式：解析文中的长难句。",
      "output_playbook": {{
          "speaking": "如果你在会议中引用此文，该如何表达。",
          "writing": "周报或邮件中可套用的高阶句型。"
      }},
      "insight": "对管理者的3点逻辑洞察。"
    }}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a professional Business English coach."},
                     {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"AI Article Error: {e}")
        return None

# 2. 书籍解析函数 (Atomic Habits 专用及通用)
def get_book_insight(book_name, author):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""
    请为经典书籍《{book_name}》（作者：{author}）制作教案。
    必须按以下 JSON 结构输出：
    {{
      "intro": "核心价值简介 (双语)。",
      "takeaways": ["重点1 (含英语关键词和管理学解析)", "重点2", "重点3"],
      "why_read": "推荐理由：为什么管理者必须读这本书？",
      "image_query": "productivity,minimalist,office"
    }}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a world-class management consultant."},
                     {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"AI Book Error: {e}")
        return None

# --- 主程序 ---
def run():
    # 数据源配置
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
    
    BOOK_LIST = [
        {"title": "Atomic Habits", "author": "James Clear", "tag": "Personal Growth"},
        {"title": "The Pyramid Principle", "author": "Barbara Minto", "tag": "Logic"},
        {"title": "High Output Management", "author": "Andrew Grove", "tag": "Leadership"}
    ]

    os.makedirs('data', exist_ok=True)
    all_articles = []
    all_books = []

    # 引擎1: 处理外刊文章
    print("🚀 启动外刊教研引擎...")
    for src in SOURCES:
        try:
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=15)
            feed = feedparser.parse(resp.content)
            if feed.entries:
                entry = feed.entries[0]
                print(f"📘 研读中: {entry.title}")
                ai_data = get_ai_article_data(entry.title)
                if ai_data:
                    ai_data.update({
                        "source": src['name'],
                        "title": entry.title,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "link": entry.link
                    })
                    all_articles.append(ai_data)
        except Exception as e:
            print(f"Source {src['name']} skip due to error: {e}")

    # 引擎2: 处理推荐书籍
    print("📚 启动书架解析引擎...")
    for b in BOOK_LIST:
        print(f"📖 正在解析名著: {b['title']}")
        insight = get_book_insight(b['title'], b['author'])
        if insight:
            # 自动匹配 Unsplash 商务图片
            img_url = f"https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80" # 备用高质量书架图
            all_books.append({
                "title": b['title'],
                "author": b['author'],
                "tag": b['tag'],
                "img": img_url,
                **insight
            })

    # --- 关键：强制保存数据 ---
    print(f"💾 正在保存数据... 文章:{len(all_articles)}, 书籍:{len(all_books)}")
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    
    with open('data/books.json', 'w', encoding='utf-8') as f:
        json.dump(all_books, f, ensure_ascii=False, indent=4)
    
    print("✅ 数据同步圆满完成！")

if __name__ == "__main__":
    run()
