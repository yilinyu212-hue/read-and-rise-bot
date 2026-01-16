import os, feedparser, requests, json, random
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a professional Business English coach."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def load_data(file):
    path = f"data/{file}"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    return []

def run():
    # 1. 自动化书籍和模型库（你可以随意添加更多名字）
    BOOK_POOL = ["Deep Work", "Grit", "Zero to One", "Thinking, Fast and Slow", "Blue Ocean Strategy"]
    MODEL_POOL = ["Eisenhower Matrix", "Pareto Principle", "OKR", "5W1H Analysis"]
    
    # 2. 抓取文章 (保持最新)
    SOURCES = [{"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"}]
    all_articles = []
    for src in SOURCES:
        feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}).content)
        if feed.entries:
            e = feed.entries[0]
            ai = get_ai_data(f"针对《{e.title}》输出教案JSON: {{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词汇','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察','logic_flow':'逻辑链'}}")
            if ai:
                ai.update({"source": src['name'], "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
                all_articles.append(ai)

    # 3. 自动累加书籍 (增量更新)
    existing_books = load_data("books.json")
    read_titles = [b['title'] for b in existing_books]
    new_books = [t for t in BOOK_POOL if t not in read_titles]
    if new_books:
        target = new_books[0] # 每次只加一本
        ai_b = get_ai_data(f"解析书籍《{target}》。JSON: {{'intro':'简介','takeaways':['重点1','重点2','重点3'],'why_read':'理由','logic_flow':'A->B->C'}}")
        if ai_b:
            existing_books.append({"title": target, "author": "Auto-Selected", "tag": "Classic", "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # 4. 自动累加思维模型 (增量更新)
    existing_models = load_data("models.json")
    model_names = [m['name'].split('(')[0].strip() for m in existing_models]
    new_models = [m for m in MODEL_POOL if m not in model_names]
    if new_models:
        target = new_models[0]
        ai_m = get_ai_data(f"解析思维模型《{target}》。英文在前。JSON: {{'name':'Name (中文)','definition':'Def (中)','how_to_use':'Use (中)','english_template':['S1','S2','S3'],'logic_flow':'Step A->B'}}")
        if ai_m: existing_models.append(ai_m)

    # 5. 保存
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open('data/books.json', 'w', encoding='utf-8') as f: json.dump(existing_books, f, ensure_ascii=False, indent=4)
    with open('data/models.json', 'w', encoding='utf-8') as f: json.dump(existing_models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
