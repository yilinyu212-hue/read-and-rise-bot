import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a world-class educator."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=90)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def run():
    # 配置要抓取的完整列表
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"}
    ]
    BOOK_LIST = [
        {"title": "Atomic Habits", "author": "James Clear", "tag": "Growth"},
        {"title": "The Pyramid Principle", "author": "Barbara Minto", "tag": "Logic"}
    ]
    MODEL_LIST = ["MECE", "SCQA", "SWOT Analysis"]

    all_articles, all_books, all_models = [], [], []

    # 1. 抓取文章
    for src in SOURCES:
        try:
            feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}, timeout=15).content)
            if feed.entries:
                e = feed.entries[0]
                p = f"针对文章《{e.title}》输出完整教案JSON。mindmap字段请按这种格式：'节点1 > 节点2, 节点1 > 节点3'。内容要求：{{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词汇','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察','mindmap':'导图字符串'}}"
                ai = get_ai_data(p)
                if ai:
                    ai.update({"source": src['name'], "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
                    all_articles.append(ai)
        except: continue

    # 2. 抓取书籍
    for b in BOOK_LIST:
        p = f"解析书籍《{b['title']}》。要求简介和重点详实。JSON: {{'intro':'详细简介','takeaways':['核心重点1','核心重点2','核心重点3'],'why_read':'推荐理由','mindmap':'核心逻辑导图字符串'}}"
        ai_b = get_ai_data(p)
        if ai_b: all_books.append({"title": b['title'], "author": b['author'], "tag": b['tag'], "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **ai_b})

    # 3. 抓取模型
    for m in MODEL_LIST:
        p = f"深度解析模型《{m}》。要求：name/definition/how_to_use 均为'English (中文)'。english_template 为3个地道句子列表。mindmap 为模型结构。JSON: {{'name':'Name (中文名)','definition':'Def (中)','how_to_use':'Use (中)','english_template':['S1','S2','S3'],'mindmap':'结构图字符串'}}"
        ai_m = get_ai_data(p)
        if ai_m: all_models.append(ai_m)

    # 强制同步保存
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, 'library.json'), 'w', encoding='utf-8') as f: json.dump(all_articles, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'books.json'), 'w', encoding='utf-8') as f: json.dump(all_books, f, ensure_ascii=False, indent=4)
    with open(os.path.join(data_dir, 'models.json'), 'w', encoding='utf-8') as f: json.dump(all_models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
