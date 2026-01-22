import openai
import json
from .crawler import fetch 

def run_rize_insight(title, content):
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    作为一名服务于顶级 CEO 的商业内参主编，请解析以下外刊素材。
    
    【核心要求】：
    1. 风格：跨界洞察、精炼、高级。
    2. 语言：中文为主，关键商业术语保留英文原词（如：Network Effects, Cognitive Load）。
    3. 视觉：严禁长句。必须使用“短行列表”形式，每行不超过 15 字，确保极强呼吸感。

    素材标题：{title}
    素材原文：{content}

    请严格按 JSON 格式输出：
    {{
        "golden_quote": "一句充满哲理的商业金句，适合发朋友圈。",
        "punchline": "一句直击管理本质的深度洞察。",
        "read": "### 🔍 核心拆解 (Core Logic)\\n- **New Trend**: 宏观动向\\n- **Case Study**: 关键公司动作\\n- **Key Data**: 核心指标/成效",
        "rise": "### 🚀 决策跃迁 (Decision Guide)\\n- **Mental Model**: 思维模型\\n- **Directives**: \\n  - [Stop] 减少低效动作\\n  - [Start] 开启战略布局"
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
        return {"punchline": "解析中", "read": "加载失败", "rise": "请重试", "golden_quote": "Stay hungry."}

def sync_global_publications():
    articles = fetch()
    processed = []
    for a in articles:
        res = run_rize_insight(a['title'], a['content'])
        processed.append({
            "title": a['title'],
            "golden_quote": res.get("golden_quote"),
            "punchline": res.get("punchline"),
            "read": res.get("read"), 
            "rise": res.get("rise")
        })
    return processed
