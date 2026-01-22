import openai
import json

def run_rize_insight(title, content, workflow_id=None):
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    你是一位顶级战略顾问。请阅读以下素材，输出中文决策内参。
    素材：{content}

    请严格按 JSON 输出，确保 key 如下：
    {{
        "punchline": "一句话爆点",
        "read": "这里写 200 字以上的中文案例拆解和逻辑分析。",
        "rise": "这里写 1 个思维模型和 3 条管理行动指令。"
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
        return {"punchline": "解析失败", "read": str(e), "rise": "检查API"}

def sync_global_publications(api_key=None, workflow_id=None):
    # 这里直接调用我们刚才写的 fetch
    articles = fetch()
    processed = []
    for a in articles:
        res = run_rize_insight(a['title'], a['content'])
        processed.append({
            "title": a['title'],
            "punchline": res.get("punchline"),
            "read": res.get("read"),
            "rise": res.get("rise")
        })
    return processed
