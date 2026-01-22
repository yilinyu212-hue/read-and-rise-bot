import openai
import json
from .crawler import fetch 

def run_rize_insight(title, source, content):
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    你是《Read & Rise》主编。请基于来自《{source}》的深度素材，生成中文决策内参。
    
    【核心要求】：
    1. 风格：跨界洞察、精炼、顶级咨询质感。
    2. 视觉：严格列表化。每行不超过 15 字，严禁长段文字。
    3. 语言：中文为主，关键商业术语保留英文原词。

    素材标题：{title}
    素材原文：{content}

    请按 JSON 输出：
    {{
        "golden_quote": "一句充满哲理的商业金句 (适合发朋友圈)",
        "punchline": "一句直击管理本质的深度洞察 (20字内)",
        "read": "### 🔍 深度拆解 (Deep Dive)\\n- **New Trend**: 趋势说明\\n- **Case Study**: 关键公司动作\\n- **Key Data**: 核心指标/成效",
        "rise": "### 🚀 决策跃迁 (Action)\\n- **Mental Model**: 思维模型名称\\n- **Directives**: \\n  - [S] 减少低效动作\\n  - [S] 开启战略布局"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"punchline": "解析中", "read": "暂无内容", "rise": "暂无行动", "golden_quote": "Stay focused."}

def sync_global_publications():
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
