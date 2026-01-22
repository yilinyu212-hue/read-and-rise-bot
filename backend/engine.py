import openai
import json
# 关键：必须从本地 crawler 导入 fetch
from .crawler import fetch 

def run_rize_insight(title, content):
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"请根据以下素材输出中文内参。素材：{content}。严格按 JSON 格式输出：{{'punchline': '...', 'read': '...', 'rise': '...'}}"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"punchline": "解析失败", "read": f"错误：{str(e)}", "rise": "请检查配置"}

def sync_global_publications():
    # 调用上面定义的 fetch
    articles = fetch()
    processed = []
    for a in articles:
        res = run_rize_insight(a['title'], a['content'])
        processed.append({
            "title": a['title'],
            "punchline": res.get("punchline", "核心洞察"),
            "read": res.get("read", "深度内容生成中"), # 确保 key 是 'read'
            "rise": res.get("rise", "行动建议")
        })
    return processed
