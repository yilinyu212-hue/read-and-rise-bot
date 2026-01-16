import os, requests, json, feedparser, uuid
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def get_ai_data(prompt):
    if not DEEPSEEK_KEY:
        print("DEBUG: Missing API Key")
        return None
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        data = res.json()
        # 核心修复：检查 choices 是否存在，若不存在则打印完整错误以供排查
        if "choices" in data:
            return json.loads(data['choices'][0]['message']['content'])
        else:
            print(f"API Error Response: {data}")
            return None
    except Exception as e:
        print(f"Connection Failed: {e}")
        return None

# 执行逻辑：只有当获取到新内容时，才更新 JSON 文件，避免清空旧数据
