import os, feedparser, requests, json, random
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# 1. 核心 AI 解析函数
def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a top-tier educator."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=90)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

# 2. 数据加载函数（防止覆盖已有内容）
def load_existing_data(filename):
    path = os.path.join(os.getcwd(), 'data', filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def run():
    # --- 自动化配置库 ---
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "Fortune", "url": "https://fortune.com/feed/"},
        {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"}
    ]
    # 待选书库 (你可以不断在这里加书名)
    MASTER_BOOK_LIST = ["Atomic Habits", "Deep Work", "The Pyramid Principle", "High Output Management", "Zero to One", "Grit", "Thinking, Fast and Slow"]
    # 待选模型库
    MASTER_MODEL_LIST = ["MECE", "SCQA", "SWOT", "OKR", "Pareto Principle", "First Principles", "Eisenhower Matrix"]

    # 加载旧数据，实现增量更新
    all_articles = [] # 文章保持每日更新最新的
    existing_books = load_existing_data('books.json')
    existing_models = load_existing_data('models.json')

    # --- 流程 A: 外刊全自动抓取 ---
    for src in SOURCES:
        try:
            feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}, timeout=15).content)
            if feed.entries:
                e = feed.entries[0]
                p = f"解析文章《{e.title}》输出讲义JSON: {{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词汇Markdown','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察','logic_flow':'逻辑链'}}"
                ai = get_ai_data(p)
                if ai:
                    ai.update({"source": src['name'], "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
                    all_articles.append(ai)
        except: continue

    # --- 流程 B: 每日一书 (若库里没有则新增) ---
    current_book_titles = [b['title'] for b in existing_books]
    new_book_candidates = [b for b in MASTER_BOOK_LIST if b not in current_book_titles]
    if new_book_candidates:
        target = new_book_candidates[0] # 每次运行选一本新书
        p = f"解析书籍《{target}》。JSON: {{'intro':'简介','takeaways':['重点1','重点2','重点3'],'why_read':'理由','logic_flow':'框架A -> B -> C'}}"
        ai_b = get_ai_data(p)
        if ai_b:
            existing_books.append({"title": target, "author": "AI Curated", "tag": "Recommended", "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # --- 流程 C: 每日一模型 (若库里没有则新增) ---
    current_model_names = [m['name'].split('(')[0].strip() for m in existing_models]
    new_model_candidates = [m for m in MASTER_MODEL_LIST if m not in current_model_names]
    if new_model_candidates:
        target = new_model_candidates[0]
        p = f"解析模型《{target}》。英文在前。JSON: {{'name':'Name (中文)','definition':'Def (中)','how_to_use':'Use (中)','english_template':['S1','S2','S3'],'logic_flow':'结构A -> B'}}"
        ai_m = get_ai_data(p)
        if ai_m: existing_models.append(ai_m)

    # --- 保存所有数据 ---
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, 'library.json'), 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'books.json'), 'w', encoding='utf-8') as f: json.dump(existing_books, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'models.json'), 'w', encoding='utf-8') as f: json.dump(existing_models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
