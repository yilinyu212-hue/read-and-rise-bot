import openai

def run_rize_insight(title_or_topic, content_or_key, workflow_id=None):
    """
    【合伙人定制版】DeepSeek 深度解析引擎
    """
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f", # <--- 必须填入你的真实 Key
        base_url="https://api.deepseek.com"
    )

    # 强化 Prompt，确保 Read 和 Rise 两个板块有血有肉
    prompt = f"""
    你是一位资深的教育者和商业教练。请根据以下外刊全文，生成中英文双语深度解析。
    要求：必须包含具体公司案例，严禁空话。

    文章标题/主题：{title_or_topic}
    文章全文素材：{content_or_key}

    ### 📘 [Read] 深度精读与案例 (Deep Dive & Cases)
    - **Core Concept**: 提取核心商业理论。
    - **Case Study**: 详细描述一个相关的真实商业案例，包含具体行动。
    
    ### 🚀 [Rise] 管理跃迁与反思 (Strategic Rise)
    - **Mental Model**: 这篇文章对应哪个思维模型？
    - **Actionable Advice**: 给管理者的 3 条具体操作建议。
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    # 返回字典格式，彻底解决 TypeError 报错
    return {
        "title": title_or_topic,
        "content": response.choices[0].message.content
    }

def sync_global_publications(api_key=None, workflow_id=None):
    """确保全球同步功能不再报错"""
    from .crawler import fetch
    return fetch()
