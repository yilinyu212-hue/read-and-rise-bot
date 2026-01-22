import openai

def run_rize_insight(title, content, workflow_id=None):
    """
    【管理者专属】DeepSeek 深度解析引擎：强制双语、强制爆点、强制思维模型
    """
    client = openai.OpenAI(
        api_key="sk-4ee83ed8d53a4390846393de5a23165f",
        base_url="https://api.deepseek.com"
    )

    # 专门为中高层管理者设计的 Prompt，杜绝废话
    prompt = f"""
    你是一位顶级战略顾问。请阅读以下外刊全文，为中高层管理者生成深度解析。
    
    外刊标题：{title}
    外刊原文：{content}

    请严格按以下格式（中英文双语）输出：

    ---
    ### 🎯 [核心爆点] Insight & Punchline
    - **中文总结**: 一句话总结此文为何值得中高层关注。
    - **Core Insight**: A powerful summary for decision makers.

    ### 📘 [Read] 深度精读与案例 Deep Dive & Case Study
    - **理论核心 (Theory)**: 文章背后的管理逻辑。
    - **实战案例 (Real Case)**: 文中提到了哪家公司/组织？他们具体是怎么做的？有什么数据结果？

    ### 🚀 [Rise] 管理跃迁与反思 Strategic Reflection
    - **思维模型 (Mental Model)**: 对应哪个经典模型（如：第二曲线、飞轮效应、反脆弱等）？
    - **行动建议 (Actionable Advice)**:
        1. 立即停止做什么？
        2. 立即开始做什么？
        3. 长期需要布局什么？
    ---
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "你是一位专注于商业深度分析的合伙人助手。"},
                      {"role": "user", "content": prompt}]
        )
        analysis_content = response.choices[0].message.content
        
        # 封装成字典，确保前端格式统一
        return {
            "title": f"[外刊精选] {title}",
            "content": analysis_content,
            "status": "success"
        }
    except Exception as e:
        return {"title": "同步失败", "content": f"AI 引擎调用出错: {str(e)}", "status": "error"}

def sync_global_publications(api_key=None, workflow_id=None):
    """确保全球同步功能能够获取全文并触发 AI 解析"""
    from .crawler import fetch
    raw_articles = fetch()
    processed_articles = []
    
    for art in raw_articles[:5]:  # 每次精选 5 篇深度解析
        res = run_rize_insight(art['title'], art['content'])
        processed_articles.append(res)
    return processed_articles
