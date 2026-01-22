import openai

def run_rize_insight(title, content, workflow_id=None):
    """
    【高管内参版】DeepSeek 引擎：内置思维模型库，强制中英双语与实战案例
    """
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", 
        base_url="https://api.deepseek.com"
    )

    # 预设中高层管理者最关注的思维模型库
    models = "第二曲线, 第一性原理, 飞轮效应, 反脆弱, 边际成本, 幸存者偏差, 冰山模型, 系统思考"

    prompt = f"""
    你是一位服务于顶级 CEO 的战略顾问。请阅读外刊全文，生成一份高价值决策内参。
    
    外刊标题：{title}
    外刊全文：{content}

    请严格按以下结构输出（中英文双语）：

    ### 🎯 [CEO 爆点] The Punchline
    - **一句话洞察**: 这篇文章揭示了什么被大多数人忽略的真相？
    - **Why it matters**: 为什么中高层必须现在关注这个信息？

    ### 📘 [Read] 深度精读：全球案例与逻辑
    - **Theory**: 核心管理理论的拆解。
    - **Case Study**: 文中具体的公司/人物案例及数据表现（必须具体）。

    ### 🚀 [Rise] 管理跃迁：思维模型与指令
    - **思维模型 (Mental Model)**: 从以下模型中选一个最匹配的并解释应用：{models}。
    - **管理者行动指令 (Directives)**:
        - [STOP] 停止哪种低效行为？
        - [START] 立即开始哪种布局？
        - [SHIFT] 思维方式应如何转变？
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "你是一位专注于商业深度分析和教育管理逻辑的合伙人。"},
                      {"role": "user", "content": prompt}],
            temperature=0.7 # 保持专业性的同时增加洞察力
        )
        return {
            "title": title,
            "content": response.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        return {"title": title, "content": f"AI 引擎调用失败: {str(e)}", "status": "error"}

def sync_global_publications(api_key=None, workflow_id=None):
    from .crawler import fetch
    return fetch()
