import openai
import json
from .crawler import fetch 

def run_rize_insight(title, content):
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    作为顶级咨询顾问，请将以下素材转化为一份高质感内参。
    
    【原则】：
    1. 关键术语保留英文原词，如：(Talent Density / 人才密度)。
    2. 严禁大段文字，必须使用 Markdown 列表(Bullet Points)。
    3. 增加“呼吸感”，每段话不超过 3 行。

    素材标题：{title}
    素材内容：{content}

    请严格按 JSON 格式输出：
    {{
        "punchline": "用一句极具爆点的话总结洞察 (20字以内)",
        "read": "### 核心逻辑\\n- **Key Insight**: 用一句话说明核心逻辑\\n- **Context (背景)**: 简单说明背景\\n- **Action (行动)**: 文中公司做了什么\\n- **Data (数据)**: 具体成效",
        "rise": "### 🚀 Actionable Advice\\n- **Mental Model (思维模型)**: 关联模型名称\\n- **Daily Directive (今日指令)**: \\n  1. [Stop] 停止的行为\\n  2. [Start] 启动的布局"
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
        return {"punchline": "解析失败", "read": "暂无数据", "rise": "暂无指令"}

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
