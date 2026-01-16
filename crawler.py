import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a world-class Business English coach."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def load_data_safe(filename):
    path = f"data/{filename}"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except: return []
    return []

def run():
    # 你的核心资产库
    BOOK_POOL = ["Atomic Habits", "The Pyramid Principle", "Deep Work", "Grit", "Zero to One"]
    MODEL_POOL = ["MECE", "SCQA", "SWOT", "OKR", "Pareto Principle"]
    
    # 1. 文章（保持最新）
    all_articles = []
    feed = feedparser.parse(requests.get("https://hbr.org/rss/topic/leadership", headers={"User-Agent": UA}).content)
    if feed.entries:
        e = feed.entries[0]
        ai = get_ai_data(f"解析文章《{e.title}》: {{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词汇','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察','logic_flow':'逻辑链'}}")
        if ai:
            ai.update({"source": "HBR", "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
            all_articles.append(ai)

    # 2. 书籍（保留旧的，新增一本）
    books = load_data_safe("books.json")
    exist_titles = [b.get('title') for b in books]
    new_books = [t for t in BOOK_POOL if t not in exist_titles]
    if new_books:
        target = new_books[0]
        ai_b = get_ai_data(f"解析书籍《{target}》: {{'intro':'简介','takeaways':['重点1','重点2','重点3'],'why_read':'理由','logic_flow':'逻辑'}}")
        if ai_b:
            books.append({"title": target, "author": "AI Coach", "tag": "Classic", "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # 3. 模型（保留旧的，新增一个）
    models = load_data_safe("models.json")
    exist_mods = [m.get('name', '').split('(')[0].strip() for m in models]
    new_mods = [m for m in MODEL_POOL if m not in exist_mods]
    if new_mods:
        target = new_mods[0]
        ai_m = get_ai_data(f"解析模型《{target}》: {{'name':'Name (中文)','definition':'Def (中)','how_to_use':'Use (中)','english_template':['S1','S2','S3'],'logic_flow':'逻辑'}}")
        if ai_m:
            models.append(ai_m)

    # 4. 强制保存
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open('data/books.json', 'w', encoding='utf-8') as f: json.dump(books, f, ensure_ascii=False, indent=4)
    with open('data/models.json', 'w', encoding='utf-8') as f: json.dump(models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
