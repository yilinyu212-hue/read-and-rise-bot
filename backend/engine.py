import openai
import json

def run_rize_insight(title, content, workflow_id=None):
    """
    【解析补丁版】确保 read 字段内容 100% 投递到前端
    """
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    你是一位顶级战略顾问。请阅读外刊全文，生成决策内参。
    标题：{title}
    全文：{content[:3000]}

    请严格按 JSON 输出：
    {{
        "punchline": "一句话核心洞察",
        "read_content": "这里写深度精读的具体案例和逻辑分析，不少于200字。",
        "rise_content": "这里写思维模型和具体行动建议。"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        res_data = json.loads(response.choices[0].message.content)
        
        # 核心修复点：确保返回的 key 与 app.py 调用的完全一致
        return {
            "punchline": res_data.get("punchline", "暂无爆点"),
            "read": res_data.get("read_content", "案例解析提取失败，请重试"), 
            "rise": res_data.get("rise_content", "行动建议生成失败")
        }
    except Exception as e:
        return {
            "punchline": "解析异常",
            "read": f"由于网络波动，深度精读内容未能加载：{str(e)}",
            "rise": "请检查后台日志"
        }

def sync_global_publications(api_key=None, workflow_id=None):
    from .crawler import fetch
    articles = fetch()
    processed = []
    # 限制处理篇数以提高响应速度
    for a in articles[:3]:
        res = run_rize_insight(a['title'], a['content'])
        # 确保这里拼装给前端的 key 叫 'read' 和 'rise'
        processed.append({
            "title": a['title'],
            "punchline": res['punchline'],
            "read": res['read'],
            "rise": res['rise']
        })
    return processed
