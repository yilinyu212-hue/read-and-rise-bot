import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a senior Business English educator."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def run():
    # --- 10个顶尖信源配置 ---
    SOURCES = [
        {"name": "HBR (领导力)", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist (简报)", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
        {"name": "WSJ (商业)", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Fortune (财富)", "url": "https://fortune.com/feed/"},
        {"name": "Forbes (创新)", "url": "https://www.forbes.com/innovation/feed/"},
        {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
        {"name": "The Atlantic", "url": "https://www.theatlantic.com/feed/all/"},
        {"name": "Wired (科技)", "url": "https://www.wired.com/feed/rss"},
        {"name": "McKinsey (麦肯锡)", "url": "https://www.mckinsey.com/insights/rss"}
    ]

    all_articles = []
    
    for src in SOURCES:
        try:
            print(f"正在抓取: {src['name']}")
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=15)
            feed = feedparser.parse(resp.content)
            
            if feed.entries:
                # 选取每个源最新的一篇
                e = feed.entries[0]
                prompt = f"针对文章《{e.title}》输出讲义JSON: {{'level':'C1','en_excerpt':'原文核心段','cn_translation':'翻译','vocabulary_pro':'关键词(英文:中文)','syntax_analysis':'句法结构','output_playbook':{{'speaking':'口语地道表达','writing':'写作高级表达'}},'insight':'教练视角的深度洞察','logic_flow':'逻辑链(A -> B -> C)'}}"
                ai = get_ai_data(prompt)
                
                if ai:
                    ai.update({
                        "source": src['name'],
                        "title": e.title,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    all_articles.append(ai)
        except Exception as ex:
            print(f"源 {src['name']} 抓取跳过: {ex}")
            continue

    # 强制保存，确保即使只有部分源成功也能显示
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

    # --- 兜底逻辑：确保书籍和模型不为空 ---
    if not os.path.exists('data/books.json') or os.path.getsize('data/books.json') < 10:
        book_init = get_ai_data("解析《Atomic Habits》: {'intro':'简介','takeaways':['1','2','3'],'why_read':'理由','logic_flow':'逻辑'}")
        if book_init:
            with open('data/books.json', 'w', encoding='utf-8') as f:
                json.dump([{"title": "Atomic Habits", "author": "James Clear", "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **book_init}], f, ensure_ascii=False)

if __name__ == "__main__":
    run()
