import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}


def analyze_article(title: str, content: str) -> dict:
    """
    输入：文章标题 + 正文
    输出：结构化分析结果
    """

    prompt = f"""
You are an analytical reading assistant for thoughtful adults.

Article title:
{title}

Article content:
{content}

Please output STRICT JSON only, with the following fields:

- cn_summary: 中文摘要（150字以内）
- en_summary: English summary (120 words max)
- core_model: 提炼一个思维模型或概念
- key_insight: 作者真正想说明的核心判断
- reflection_question: 一个值得读者反思的问题

Output JSON only. Do not include explanations.
"""

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()

    raw_text = response.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "error": "JSON parse failed",
            "raw_output": raw_text
        }
