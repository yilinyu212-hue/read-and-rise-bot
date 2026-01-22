import openai
import json
from .crawler import fetch 

def run_rize_insight(title, source, content):
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    作为《Read & Rise》主编，请解析来自《{source}》的深度素材。
    要求：1. 列表化；2. 中英对照关键术语；3. 每行短小。

    素材标题：{title}
    素材原文：{content}

    请按 JSON 格式输出：
    {{
        "golden_quote": "适合发朋友圈的金句",
        "punchline": "直击本质的洞察",
        "read": "### 🔍 深度拆解\\n- **核心观点**: XXX\\n- **关键案例**: XXX",
        "rise": "### 🚀 决策行动\\n- **思维模型**: XXX\\n- **Start/Stop**: XXX"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"golden_quote": "Stay hungry.", "punchline": "解析中", "read": "暂无", "rise": "暂无"}

def sync_global_publications():
    """这是 app.py 调用的核心函数名"""
    articles = fetch()
    processed = []
    for a in articles:
        res = run_rize_insight(a['title'], a['source'], a['content'])
        processed.append({
            **a,
            "golden_quote": res.get("golden_quote"),
            "punchline": res.get("punchline"),
            "read": res.get("read"), 
            "rise": res.get("rise")
        })
    return processed
