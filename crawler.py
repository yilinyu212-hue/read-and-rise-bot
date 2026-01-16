import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a senior educator."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def save_json(filename, data):
    os.makedirs('data', exist_ok=True)
    with open(f'data/{filename}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def run():
    # 1. 抓取外刊
    articles = []
    feed = feedparser.parse(requests.get("https://hbr.org/rss/topic/leadership", headers={"User-Agent": UA}).content)
    if feed.entries:
        e = feed.entries[0]
        ai = get_ai_data(f"解析文章《{e.title}》输出讲义JSON: {{'level':'C1','en_excerpt':'原文','cn_translation':'翻译','vocabulary_pro':'词汇','syntax_analysis':'句法','output_playbook':{{'speaking':'口语','writing':'写作'}},'insight':'洞察','logic_flow':'逻辑链'}}")
        if ai:
            ai.update({"source": "HBR", "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
            articles.append(ai)
    save_json('library.json', articles)

    # 2. 初始书籍 (直接生成，确保不为空)
    book_ai = get_ai_data("解析《Atomic Habits》: {{'intro':'简介','takeaways':['1','2','3'],'why_read':'理由','logic_flow':'逻辑'}}")
    if book_ai:
        books = [{"title": "Atomic Habits", "author": "James Clear", "tag": "Growth", "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800", **book_ai}]
        save_json('books.json', books)

    # 3. 初始模型
    model_ai = get_ai_data("解析《MECE》: {{'name':'MECE (相互独立，完全穷尽)','definition':'定义','how_to_use':'用法','english_template':['S1','S2'],'logic_flow':'逻辑'}}")
    if model_ai:
        save_json('models.json', [model_ai])

if __name__ == "__main__": run()
