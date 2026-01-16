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
    # 1. 任务清单
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"}
    ]
    BOOK_LIST = [
        {"title": "Atomic Habits", "author": "James Clear", "tag": "Personal Growth"},
        {"title": "The Pyramid Principle", "author": "Barbara Minto", "tag": "Logic"}
    ]
    MODEL_LIST = ["MECE", "First Principles", "SCQA"]

    all_articles, all_books, all_models = [], [], []

    # 引擎 A：精读文章
    for src in SOURCES:
        try:
            feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}, timeout=15).content)
            if feed.entries:
                entry = feed.entries[0]
                ai = get_ai_data(f"针对《{entry.title}》输出讲义JSON: {{'level':'C1','en_excerpt':'原文段落','cn_translation':'段落翻译','vocabulary_pro':'重点词汇Markdown','syntax_analysis':'句法拆解Markdown','output_playbook':{{'speaking':'口语话术','writing':'写作句型'}},'insight':'教练洞察'}}")
                if ai:
                    ai.update({"source": src['name'], "title": entry.title, "date": datetime.now().strftime("%Y-%m-%d")})
                    all_articles.append(ai)
        except: continue

    # 引擎 B：名著书籍
    for b in BOOK_LIST:
        ai_b = get_ai_data(f"为书籍《{b['title']}》输出教案JSON: {{'intro':'简介','takeaways':['重点1','重点2','重点3'],'why_read':'推荐理由'}}")
        if ai_b:
            all_books.append({"title": b['title'], "author": b['author'], "tag": b['tag'], "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # 引擎 C：思维模型 (优化排版：英文在前)
    for m in MODEL_LIST:
        ai_m = get_ai_data(f"解析思维模型《{m}》。要求所有描述均为'英文说明 (中文翻译)'格式。输出JSON: {{'name':'英文名 (中文名)','definition':'English Definition (中文定义)','how_to_use':'English Scenario (应用场景中文)','english_template':'3段高阶演讲例句'}}")
        if ai_m:
            all_models.append(ai_m)

    # 保存
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, 'library.json'), 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'books.json'), 'w', encoding='utf-8') as f: json.dump(all_books, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'models.json'), 'w', encoding='utf-8') as f: json.dump(all_models, f, ensure_ascii=False, indent=4)
    print("Update Successful")

if __name__ == "__main__": run()
