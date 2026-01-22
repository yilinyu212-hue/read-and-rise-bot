import openai

def analyze_article(title, content):
    """
    对接 DeepSeek 大脑，生成 Read & Rise 深度解析内容
    """
    prompt = f"""
    你是一位资深的教育者和商业教练。请根据以下外刊全文内容，为‘Read & Rise’平台生成深度内容。
    
    文章标题：{title}
    文章全文：{content}
    
    请严格按照以下板块输出（使用中英文双语）：

    ### 📘 [Read] 深度精读与案例
    - **Core Concept (核心概念)**: 提取文章最核心的一个理论。
    - **Case Study (案例解析)**: 详细描述文中的公司或人物案例。
    
    ### 🚀 [Rise] 管理跃迁与反思
    - **Mental Model (思维模型)**: 这篇文章对应哪个经典的商业思维模型？
    - **Actionable Advice (行动建议)**: 给教育者/管理者的 3 条具体操作建议。
    """
    
    client = openai.OpenAI(
        api_key="你的DEEPSEEK_API_KEY", # 这里请确保填入你的 Key
        base_url="https://api.deepseek.com"
    )
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
