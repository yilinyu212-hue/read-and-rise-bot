import os, feedparser, requests, json, uuid
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {
        "model": "deepseek-chat", 
        "messages": [
            {"role": "system", "content": "You are a world-class Business English Coach and Educator. Your goal is to deconstruct complex articles into high-end learning materials for executives."},
            {"role": "user", "content": prompt}
        ], 
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return None

def run():
    # 1. 扩充信源 (确保内容多样性)
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"}
    ]
    
    all_articles = []
    
    # 2. 深度解析逻辑 (核心升级)
    for src in SOURCES:
        try:
            resp = requests.get(src['url'], headers={"User-Agent": UA}, timeout=15)
            feed = feedparser.parse(resp.content)
            
            if feed.entries:
                e = feed.entries[0] # 取每个源最新的一篇
                
                # 强化 Prompt：明确词汇、双语和句法的输出格式
                prompt = f"""
                Analyze the article: "{e.title}"
                Output a JSON object with the following fields:
                1. "level": English level (e.g., B2, C1)
                2. "en_excerpt": A 100-word core paragraph from the article.
                3. "cn_translation": Precise Chinese translation of the excerpt.
                4. "vocabulary_pro": 5-8 key business terms in the format "word: translation, word2: translation".
                5. "syntax_analysis": Explain one complex sentence structure found in the excerpt.
                6. "insight": One high-level management insight for educators.
                7. "logic_flow": A list of 3-4 steps showing the article's logic (e.g., ["Problem Identified", "Strategic Approach", "Expected Result"]).
                8. "output_playbook": {{"speaking": "A native-like phrase for meetings", "writing": "A professional email sentence"}}.
                """
                
                ai = get_ai_data(prompt)
                if ai:
                    ai.update({
                        "id": str(uuid.uuid4())[:8],
                        "source": src['name'],
                        "title": e.title,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    all_articles.append(ai)
        except Exception as ex:
            print(f"Skip {src['name']}: {ex}")

    # 保存外刊数据
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

    # 3. 完善书籍部分 (同样增加逻辑链和深度简介)
    BOOK_TARGETS = ["The Pyramid Principle", "Atomic Habits"]
    existing_books = []
    if os.path.exists('data/books.json'):
        with open('data/books.json', 'r', encoding='utf-8') as f:
            try: existing_books = json.load(f)
            except: existing_books = []

    for book_name in BOOK_TARGETS:
        if not any(b['title'] == book_name for b in existing_books):
            book_prompt = f"Analyze book '{book_name}' in JSON: {{'intro':'Bilingual summary','takeaways':['point1','point2'],'why_read':'Value','logic_flow':['concept','structure','application']}}"
            ai_book = get_ai_data(book_prompt)
            if ai_book:
                existing_books.append({
                    "title": book_name,
                    "img": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400",
                    **ai_book
                })
    
    with open('data/books.json', 'w', encoding='utf-8') as f:
        json.dump(existing_books, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
