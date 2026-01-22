import openai

def run_rize_insight(title_or_topic, content_or_key, workflow_id=None):
    """
    兼容精准研究和全球同步两种调用模式。
    """
    client = openai.OpenAI(
        api_key="sk-0e2da60735ee494e9ff1d3d0f4185239", # <--- 请在此处粘贴你的 Key
        base_url="https://api.deepseek.com"
    )

    # 自动识别是‘精准研究’还是‘全刊同步’
    is_sync = workflow_id is None
    
    prompt = f"""
    你是一位资深的教育者和商业教练。请根据以下内容，为 'Read & Rise' 平台生成深度中英文双语解析。
    要求：必须包含具体公司或人物案例。

    主题/标题：{title_or_topic}
    内容素材：{content_or_key}

    ### 📘 [Read] 深度精读与案例 (Deep Dive & Cases)
    - **Core Concept**: 提取文章最核心的一个理论。
    - **Case Study**: 详细描述一个相关的真实商业案例，包含具体数据或行动。
    
    ### 🚀 [Rise] 管理跃迁与反思 (Strategic Rise)
    - **Mental Model**: 这篇文章对应哪个思维模型？
    - **Actionable Advice**: 给管理者的 3 条具体操作建议。
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def sync_global_publications(api_key=None, workflow_id=None):
    """
    兼容前端调用，获取最新 10 个外刊源全文。
    """
    from .crawler import fetch
    return fetch()
