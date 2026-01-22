import openai

def run_rize_insight(title, content, workflow_id=None):
    """
    【Read & Rise 核心引擎】
    将外刊全文转化为结构化的高管内参。
    """
    client = openai.OpenAI(
        api_key="在此粘贴你的_DEEPSEEK_API_KEY", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    你是一位服务于顶级 CEO 的战略顾问。请阅读外刊全文，生成一份结构化的决策内参。
    
    外刊标题：{title}
    外刊全文：{content}

    请严格按以下格式输出（不要任何多余的解释，确保是标准的 Python 字典格式）：
    {{
        "punchline": "用中文写出一句话爆点洞察，点透对中高层的核心价值。",
        "read_content": "### 📘 [Read] 案例拆解\\n- **核心逻辑**: 中文解析。\\n- **实战案例**: 必须包含文中提到的公司、数据或具体行动（中英双语）。",
        "rise_content": "### 🚀 [Rise] 管理行动\\n- **思维模型**: 关联一个经典商业模型。\\n- **指令**: 给出1条STOP(停止)、1条START(开始)建议。"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" } # 强制返回 JSON
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "punchline": "同步暂时中断",
            "read_content": f"AI 解析出错: {str(e)}",
            "rise_content": "请检查 API Key 或网络连接。"
        }

def sync_global_publications(api_key=None, workflow_id=None):
    from .crawler import fetch
    raw_data = fetch()
    processed = []
    # 每次处理前 5 篇最深度文章，确保质量
    for item in raw_data[:5]:
        analysis = run_rize_insight(item['title'], item['content'])
        # 整合数据提供给前端
        processed.append({
            "title": item['title'],
            "punchline": analysis.get("punchline"),
            "read": analysis.get("read_content"),
            "rise": analysis.get("rise_content")
        })
    return processed
