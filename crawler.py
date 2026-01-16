import os, requests, json, feedparser, uuid, time
from datetime import datetime

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def ask_ai(prompt):
    if not API_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are an Elite Business Educator. Output strictly in JSON."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except: return None

def run():
    os.makedirs("data", exist_ok=True)
    
    # 1. 外刊逻辑 (之前已完善，保持 10 个源)
    # ... (此处省略重复的外刊代码)

    # 2. 书籍逻辑 (我们要确保 AI 每次都生成最新的书籍导读)
    books_list = ["The Pyramid Principle", "Atomic Habits", "Thinking, Fast and Slow", "Blue Ocean Strategy"]
    book_results = []
    for b_name in books_list:
        print(f"Analyzing Book: {b_name}")
        prompt = f"""Analyze the business book '{b_name}'. 
        Output JSON: {{
            "title": "{b_name}",
            "intro": "A 50-word high-level introduction",
            "takeaways": ["Point 1", "Point 2", "Point 3"],
            "coach_tips": "Practical advice for a CEO reading this book"
        }}"""
        res = ask_ai(prompt)
        if res: book_results.append(res)
    
    # 保存数据
    with open("data/books.json", "w", encoding="utf-8") as f:
        json.dump(book_results, f, ensure_ascii=False, indent=4)
    
    # 模型逻辑
    models_data = [{"name": "SCQA Framework", "scenario": "High-stakes presentation", "coach_tips": "Focus on the 'Complication' to build tension."}]
    with open("data/models.json", "w", encoding="utf-8") as f:
        json.dump(models_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
