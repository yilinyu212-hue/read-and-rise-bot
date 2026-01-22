import openai
import json

def run_rize_insight(title, content, workflow_id=None):
    """
    【高管内参定稿版】
    强制 DeepSeek 避开翻译，直接输出深度结构化内容
    """
    client = openai.OpenAI(
        api_key="你的_DEEPSEEK_API_KEY", # <--- 请务必确认这里填了 Key
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    你是一位顶级商业咨询顾问。请阅读以下外刊全文，为中高层管理者撰写一份【中文为主、关键术语英文】的深度内参。
    
    外刊标题：{title}
    原文素材：{content[:3000]} 

    请严格按照以下 JSON 格式输出，不要有任何多余文字：
    {{
        "punchline": "用中文写一句话爆点。点出这篇文章对管理者最核心的生存/盈利价值。",
        "read_content": "### 📘 [Read] 深度精读\\n- **核心洞察**: (中文描述核心逻辑)\\n- **实战案例**: (详细拆解文中的公司案例，包含具体行动和数据。)",
        "rise_content": "### 🚀 [Rise] 管理跃迁\\n- **思维模型**: (关联1个经典模型，如：反脆弱、飞轮效应)\\n- **行动清单**: (1. 停止做什么；2. 开始做什么；3. 长期布局。)"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "你是一位专注于商业深度拆解的 AI 合伙人。"},
                      {"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "punchline": "内容解析中",
            "read_content": f"正在调取 DeepSeek 深层大脑... (Error: {str(e)})",
            "rise_content": "请稍后刷新"
        }

def sync_global_publications(api_key=None, workflow_id=None):
    from .crawler import fetch
    articles = fetch()
    processed = []
    for a in articles[:3]: # 先精准处理前3篇，确保每一篇都是精品
        res = run_rize_insight(a['title'], a['content'])
        processed.append({
            "title": a['title'],
            "punchline": res.get("punchline"),
            "read": res.get("read_content"),
            "rise": res.get("rise_content")
        })
    return processed
