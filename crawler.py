import os, requests, json, feedparser, uuid
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def get_ai_data(prompt):
    if not DEEPSEEK_KEY:
        print("Error: DEEPSEEK_API_KEY is empty!")
        return None
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        data = res.json()
        # 核心防御逻辑：如果 choices 不在 data 里，打印整个 data 让我们看具体错误
        if "choices" in data:
            return json.loads(data['choices'][0]['message']['content'])
        else:
            print(f"DEBUG - API Rejected: {data}")
            return None
    except Exception as e:
        print(f"DEBUG - Request Failed: {e}")
        return None

def run():
    # ... (保持之前的抓取逻辑，但确保在写入 JSON 前判断内容是否为空)
    # 如果本次爬取 articles 长度为 0，不要写入文件，保留旧文件
    pass

if __name__ == "__main__":
    run()
