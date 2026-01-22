import openai

def run_rize_insight(title_or_topic, content_or_key, workflow_id=None):
    """
    合伙人定制版：对接 DeepSeek，生成 Read & Rise 深度中英双语解析
    """
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", # <--- 请在此粘贴你的 Key
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    你是一位资深的教育者和商业教练。请根据以下内容，为 'Read & Rise' 平台生成深度内容。
    要求：必须包含具体公司或人物案例，使用中英文双语。

    主题/素材：{title_or_topic}
    详细背景：{content_or_key}

    ### 📘 [Read] 深度精读与案例 (Deep Dive & Cases)
    - **Core Concept**: 提取文章最核心的一个理论。
    - **Case Study**: 详细描述一个相关的真实商业案例。
    
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
    兼容前端调用，确保‘全球同步’功能正常运行
    """
    from .crawler import fetch
    return fetch()
