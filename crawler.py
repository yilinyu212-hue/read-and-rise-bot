import os, feedparser, requests, json, uuid
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {
        "model": "deepseek-chat", # 确认模型名称正确
        "messages": [
            {"role": "system", "content": "You are a professional Executive Coach. Output strictly in JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"} # 强制 JSON 输出
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        res_json = res.json()
        if "choices" in res_json:
            return json.loads(res_json['choices'][0]['message']['content'])
        else:
            # 这行会在 GitHub Action 日志里打印具体错在哪里
            print(f"API Error Details: {res_json}")
            return None
    except Exception as e:
        print(f"Request Error: {e}")
        return None
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {
        "model": "deepseek-chat", 
        "messages": [
            {"role": "system", "content": "You are a professional Executive Coach. Output strictly in valid JSON format."},
            {"role": "user", "content": prompt}
        ], 
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        res_json = res.json()
        # 核心修复：检查 choices 是否在返回结果中
        if "choices" in res_json:
            return json.loads(res_json['choices'][0]['message']['content'])
        else:
            print(f"API Error Response: {res_json}") # 打印出具体的错误原因
            return None
    except Exception as e:
        print(f"Request Exception: {e}")
        return None

def run():
    # 1. 处理外刊数据
    articles = []
    feed = feedparser.parse(requests.get("https://hbr.org/rss/topic/leadership", headers={"User-Agent": UA}).content)
    
    if feed.entries:
        for e in feed.entries[:3]:
            prompt = f"Deconstruct article '{e.title}' into: {{'level':'C1','en_excerpt':'paragraph','cn_translation':'translation','vocabulary_pro':'word:mean','syntax_analysis':'analysis','logic_flow':['step1','step2'],'insight':'tip','output_playbook':{{'speaking':'phrase','writing':'sentence'}}}}"
            ai = get_ai_data(prompt)
            if ai:
                ai.update({"id": str(uuid.uuid4())[:8], "source": "HBR", "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
                articles.append(ai)
    
    # 2. 如果本次 AI 失败，尝试读取旧数据兜底，不让页面变白
    os.makedirs('data', exist_ok=True)
    if not articles and os.path.exists('data/library.json'):
        print("Using cached data for Library...")
    else:
        with open('data/library.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)

    # 3. 处理思维模型 (增加稳定性)
    models = []
    MODEL_POOL = ["MECE Principle", "SCQA Framework", "Pareto Principle"]
    for m_name in MODEL_POOL:
        m_prompt = f"Analyze model '{m_name}': {{'name':'Name','definition':'Def','scenario':'Scene','logic_flow':['A','B'],'english_template':['T1','T2'],'coach_tips':'Tip'}}"
        ai_m = get_ai_data(m_prompt)
        if ai_m:
            models.append(ai_m)
    
    if models:
        with open('data/models.json', 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
