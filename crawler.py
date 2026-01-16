import os
import feedparser
import requests
import json
import uuid
import time
from datetime import datetime

# --- 配置区 ---
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
DATA_DIR = "data"

def get_ai_data(prompt):
    """带容错机制的 AI 请求函数"""
    if not DEEPSEEK_KEY:
        print("CRITICAL: DEEPSEEK_API_KEY is not set in GitHub Secrets!")
        return None
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional Executive Coach. Output strictly in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        res_json = response.json()
        
        # 核心修复：安全检查 choices 字段
        if "choices" in res_json:
            content = res_json['choices'][0]['message']['content']
            return json.loads(content)
        else:
            print(f"API Error Response: {res_json}")
            return None
    except Exception as e:
        print(f"Request Exception: {e}")
        return None

def run_sync():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"--- Task Started: {datetime.now()} ---")

    # 1. 抓取外刊精读 (HBR 为例)
    articles = []
    feed_url = "https://hbr.org/rss/topic/leadership"
    try:
        feed = feedparser.parse(requests.get(feed_url, headers={"User-Agent": UA}, timeout=15).content)
        if feed.entries:
            for e in feed.entries[:3]: # 每次更新最新3篇
                print(f"Processing Article: {e.title}")
                prompt = f"""
                Analyze the business article: "{e.title}"
                Output a JSON with:
                - "level": "C1" or "B2"
                - "en_excerpt": "A core 100-word paragraph"
                - "cn_translation": "Precise Chinese translation"
                - "vocabulary_pro": "word: translation, word2: translation (list 5-8 keys)"
                - "syntax_analysis": "Explain one complex sentence structure"
                - "logic_flow": ["Point A", "Point B", "Point C"]
                - "insight": "Executive coaching tip"
                - "output_playbook": {{"speaking": "oral template", "writing": "email template"}}
                """
                ai_res = get_ai_data(prompt)
                if ai_res:
                    ai_res.update({
                        "id": str(uuid.uuid4())[:8],
                        "source": "Harvard Business Review",
                        "title": e.title,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    articles.append(ai_res)
    except Exception as ex:
        print(f"Feed Error: {ex}")

    # 保存外刊数据：仅在抓取成功时写入，防止覆盖成空
    if articles:
        with open(f"{DATA_DIR}/library.json", 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(articles)} articles.")

    # 2. 抓取思维模型 (Management Models)
    models = []
    MODEL_LIST = ["MECE Principle", "SCQA Framework", "Pareto Principle", "First Principles Thinking"]
    for m_name in MODEL_LIST:
        print(f"Processing Model: {m_name}")
        m_prompt = f"""
        Analyze the mental model "{m_name}" for business leaders.
        Output JSON:
        - "name": "English & Chinese Name"
        - "definition": "Bilingual definition"
        - "scenario": "Specific business case study"
        - "logic_flow": ["Component 1", "Component 2", "Component 3"]
        - "english_template": ["Meeting phrase 1", "Presentation phrase 2"]
        - "coach_tips": "Common pitfalls and expert advice"
        """
        ai_m = get_ai_data(m_prompt)
        if ai_m:
            models.append(ai_m)
    
    if models:
        with open(f"{DATA_DIR}/models.json", 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(models)} models.")

    # 3. 书籍推荐 (Books)
    books = []
    BOOK_LIST = ["The Pyramid Principle", "Atomic Habits", "Thinking, Fast and Slow"]
    for b_name in BOOK_LIST:
        b_prompt = f"Analyze book '{b_name}' in JSON: {{'title':'{b_name}','intro':'Bilingual summary','takeaways':['point1','point2'],'logic_flow':['A','B','C'],'img':'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400'}}"
        ai_b = get_ai_data(b_prompt)
        if ai_b:
            books.append(ai_b)
            
    if books:
        with open(f"{DATA_DIR}/books.json", 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=4)

    print("--- All Tasks Completed ---")

if __name__ == "__main__":
    run_sync()
