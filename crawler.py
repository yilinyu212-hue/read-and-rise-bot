import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a professional Business English coach."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def run():
    # 1. 配置：文章、书籍、思维模型
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"}
    ]
    BOOK_LIST = [
        {"title": "Atomic Habits", "author": "James Clear", "tag": "Personal Growth"}
    ]
    # 【新板块】以后想加模型，直接往这个括号里填名字
    MODEL_LIST = ["MECE", "First Principles", "SCQA"]

    all_articles, all_books, all_models = [], [], []

    # 引擎 A：外刊
    for src in SOURCES:
        try:
            feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}, timeout=15).content)
            if feed.entries:
                entry = feed.entries[0]
                ai = get_ai_data(f"针对《{entry.title}》输出教案JSON: {{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词汇','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察'}}")
                if ai:
                    ai.update({"source": src['name'], "title": entry.title, "date": datetime.now().strftime("%Y-%m-%d")})
                    all_articles.append(ai)
        except: continue

    # 引擎 B：书籍
    for b in BOOK_LIST:
        ai_b = get_ai_data(f"为书籍《{b['title']}》输出教案JSON: {{'intro':'简介','takeaways':['重点1','重点2','重点3'],'why_read':'理由'}}")
        if ai_b:
            all_books.append({"title": b['title'], "author": b['author'], "tag": b['tag'], "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # 引擎 C：思维模型（新功能）
    for m in MODEL_LIST:
        ai_m = get_ai_data(f"请详细解析思维模型《{m}》。输出教案JSON: {{'name':'模型中文名','definition':'双语定义','how_to_use':'职场应用场景','english_template':'如果你在演讲中使用此模型，请给出3个高阶英语句型'}}")
        if ai_m:
            all_models.append(ai_m)

    # 保存数据
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, 'library.json'), 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'books.json'), 'w', encoding='utf-8') as f: json.dump(all_books, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'models.json'), 'w', encoding='utf-8') as f: json.dump(all_models, f, ensure_ascii=False, indent=4)
    print("All Data Updated!")

if __name__ == "__main__": run()
