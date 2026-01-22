import openai
import json
from .crawler import fetch 

def run_rize_insight(title, content):
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    作为一名顶级商业内参主编，请解析以下外刊素材。
    
    【核心要求】：
    1. 风格：专业、精炼、高级。
    2. 语言：中文为主，关键商业术语保留英文原词（如：Flywheel Effect, Optionality）。
    3. 结构：严禁大段长句。使用列表形式，每行不超过 20 字，确保视觉上有“呼吸感”。

    素材标题：{title}
    素材原文：{content}

    请严格按 JSON 格式输出：
    {{
        "punchline": "一句直戳管理者痛点的商业洞察。",
        "read": "### 核心逻辑 (Core Logic)\\n- **趋势**: 说明宏观动向\\n- **案例**: 具体公司/项目做了什么\\n- **数据**: 1-2个核心指标",
        "rise": "### 决策指南 (Decision Guide)\\n- **思维模型**: 关联1个跨界模型\\n- **行动建议**:\\n  - [S] 停止无效动作\\n  - [S] 启动战略布局"
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
        return {"punchline": "解析中", "read": "加载失败", "rise": "请重试"}

def sync_global_publications():
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
