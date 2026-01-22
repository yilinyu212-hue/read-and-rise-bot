import openai

def run_rize_insight(title, content):
    """
    对接 DeepSeek，生成 Read & Rise 深度解析
    """
    client = openai.OpenAI(
        api_key="sk-0e2da60735ee494e9ff1d3d0f4185239", # <--- 请在此处粘贴你的 Key
        base_url="https://api.deepseek.com"
    )

    prompt = f"""
    你是一位资深的教育者。请根据以下外刊全文，为 'Read & Rise' 平台生成深度内容。
    要求：使用中英文双语，包含具体案例。

    文章标题：{title}
    文章内容：{content}

    ### 📘 [Read] 深度精读与案例 (Deep Dive & Cases)
    - **Core Concept**: 提取核心理论。
    - **Case Study**: 详细描述文中的真实案例。

    ### 🚀 [Rise] 管理跃迁与反思 (Strategic Rise)
    - **Mental Model**: 对应哪个思维模型？
    - **Actionable Advice**: 给管理者的 3 条具体建议。
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def sync_global_publications():
    """兼容 app.py 的导入需求"""
    from .crawler import fetch
    return fetch()
