import os, feedparser, requests, json
from datetime import datetime

# --- 配置区 ---
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# 文章 AI 解析函数
def get_ai_article_data(title):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""作为顶级英语培训师，请针对《{title}》输出 JSON：
    {{
      "level": "Advanced (C1)", 
      "tags": ["Leadership", "Strategy"],
      "en_excerpt": "挑选文中60-100字核心段落。",
      "cn_translation": "专家级中文翻译。",
      "vocabulary_pro": "3个高阶词汇及应用。",
      "syntax_analysis": "长难句拆解。",
      "output_playbook": {{"speaking": "口语引用模板", "writing": "写作高阶句型"}},
      "insight": "对管理者的3点洞察。"
    }}"""
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return {}

# 书籍 AI 解析函数
def get_book_insight(book_name, author):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""请为经典书籍《{book_name}》（作者：{author}）制作教案 JSON：
    {{
      "intro": "核心价值简介 (双语)。",
      "takeaways": ["重点1(含英语关键词)", "重点2", "重点3"],
      "why_read": "推荐理由：管理者为何必读？",
      "image_query": "business,habits"
    }}"""
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return {}

def run():
    # 8 大核心信源
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
    
    # 自动生成的书单
    BOOK_LIST = [
        {"title": "Atomic Habits", "author": "James Clear", "tag": "Personal Growth"},
        {"title": "The Pyramid Principle", "author": "Barbara Minto", "tag": "Logic"},
        {"title": "High Output Management", "author": "Andrew Grove", "tag": "Leadership"}
    ]

    os.makedirs('data', exist_ok=True)

    # 抓取文章
    all_articles = []
    for src in SOURCES:
        try:
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=15)
            feed = feedparser.parse(resp.content)
            if feed.entries:
                entry = feed.entries[0]
                ai_data = get_ai_article_data(entry.title)
                if ai_data:
                    ai_data.update({"source": src['name'], "title": entry.title, "date": datetime.now().strftime("%Y-%m-%d")})
                    all_articles.append(ai_data)
        except: continue

    # 解析书籍
    all_books = []
    for b in BOOK_LIST:
        insight = get_book_insight(b['title'], b['author'])
        img_url = f"https://source.unsplash.com/800x600/?{insight.get('image_query', 'business')}"
        all_books.append({"title": b['title'], "author": b['author'], "tag": b['tag'], "img": img_url, **insight})

    with open('data/library.json', 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open('data/books.json', 'w', encoding='utf-8') as f: json.dump(all_books, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
