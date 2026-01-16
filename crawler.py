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
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def load_local_data(filename):
    path = f"data/{filename}"
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                return json.loads(content) if content.strip() else []
        except: return []
    return []

def run():
    # --- 自动化内容池 ---
    BOOK_POOL = ["Deep Work", "Grit", "Zero to One", "Thinking, Fast and Slow", "Atomic Habits", "The Pyramid Principle"]
    MODEL_POOL = ["MECE", "SCQA", "SWOT", "OKR", "Pareto Principle", "First Principles"]
    SOURCES = [{"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"}]

    # A. 抓取外刊 (每日更新)
    all_articles = []
    for src in SOURCES:
        feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}).content)
        if feed.entries:
            e = feed.entries[0]
            ai = get_ai_data(f"解析文章《{e.title}》: {{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词语','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察','logic_flow':'逻辑链'}}")
            if ai:
                ai.update({"source": src['name'], "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
                all_articles.append(ai)

    # B. 增量更新书籍 (保留旧的，新增一本)
    existing_books = load_local_data("books.json")
    read_titles = [b['title'] for b in existing_books]
    new_books = [t for t in BOOK_POOL if t not in read_titles]
    if new_books:
        target = new_books[0]
        ai_b = get_ai_data(f"详细拆解书籍《{target}》: {{'intro':'简介','takeaways':['重点1','重点2','重点3'],'why_read':'推荐理由','logic_flow':'逻辑链'}}")
        if ai_b:
            existing_books.append({"title": target, "author": "AI Curated", "tag": "Classic", "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # C. 增量更新思维模型 (保留旧的，新增一个)
    existing_models = load_local_data("models.json")
    model_names = [m.get('name','').split('(')[0].strip() for m in existing_models]
    new_models = [m for m in MODEL_POOL if m not in model_names]
    if new_models:
        target = new_models[0]
        ai_m = get_ai_data(f"解析模型《{target}》: {{'name':'Name (中文)','definition':'Def (中)','how_to_use':'Use (中)','english_template':['S1','S2','S3'],'logic_flow':'结构'}}")
        if ai_m: existing_models.append(ai_m)

    # --- 统一保存 ---
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open('data/books.json', 'w', encoding='utf-8') as f: json.dump(existing_books, f, ensure_ascii=False, indent=4)
    with open('data/models.json', 'w', encoding='utf-8') as f: json.dump(existing_models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
