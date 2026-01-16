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
    SOURCES = [{"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"}]
    BOOK_LIST = [{"title": "Atomic Habits", "author": "James Clear", "tag": "Growth"}]
    MODEL_LIST = ["MECE", "SCQA"]

    all_articles, all_books, all_models = [], [], []

    # 1. 文章
    for src in SOURCES:
        try:
            feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}, timeout=15).content)
            if feed.entries:
                e = feed.entries[0]
                ai = get_ai_data(f"针对《{e.title}》输出讲义JSON: {{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词汇','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察'}}")
                if ai:
                    ai.update({"source": src['name'], "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
                    all_articles.append(ai)
        except: continue

    # 2. 书籍
    for b in BOOK_LIST:
        ai_b = get_ai_data(f"为书籍《{b['title']}》输出教案JSON: {{'intro':'简介','takeaways':['重点1','重点2','重点3'],'why_read':'理由'}}")
        if ai_b:
            all_books.append({"title": b['title'], "author": b['author'], "tag": b['tag'], "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # 3. 思维模型 (强制英文在前)
    for m in MODEL_LIST:
        p = f"解析模型《{m}》。要求：name/definition/how_to_use 均采用 'English (中文)' 格式。english_template 为3个纯英文地道句型列表。JSON: {{'name':'Name (中文名)','definition':'Eng definition (中文定义)','how_to_use':'Eng scenario (应用场景中文)','english_template':['Sentence 1','Sentence 2','Sentence 3']}}"
        ai_m = get_ai_data(p)
        if ai_m: all_models.append(ai_m)

    # 强制路径并保存
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, 'library.json'), 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'books.json'), 'w', encoding='utf-8') as f: json.dump(all_books, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'models.json'), 'w', encoding='utf-8') as f: json.dump(all_models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
