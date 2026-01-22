import requests
import os
import json

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

SYSTEM_PROMPT = """（这里粘贴我刚才给你的完整 Prompt）"""

def analyze_article(title: str, summary: str = "") -> dict:
    user_input = f"""
英文文章标题：
{title}

文章摘要（如有）：
{summary}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {sk-4ee83ed8d53a4390846393de5a23165f}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)
