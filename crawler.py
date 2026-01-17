import os
import requests
import json

# 配置环境变量
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

def get_ai_insight(title, content):
    """
    调用 AI 对抓取的文章进行深度萃取。
    这里增加了对“原文摘录”和“中英对照”的强制要求。
    """
    # 这里建议你在 GitHub Secrets 里也配置一个你的 AI_API_KEY
    # 暂时用伪代码展示逻辑，你需要确保你的 AI 调用部分能处理以下 Prompt
    prompt = f"""
    作为 Read & Rise 的教育者，请深度解析《{title}》：
    
    1. [Original_Quotes]: 请直接从原文中摘录 3 段最有战略深度的英文原文 (Verbatim)。
    2. [Chinese_Insight]: 用 150 字以内的中文提炼核心管理洞察。
    3. [Lingo_Lab]: 提取 2 个商业场景下的高管级词汇及其用法。
    4. [Socratic_Question]: 提出 1 个让 Leader 感到“痛”的反思问题。
    
    文章内容: {content[:2000]} 
    """
    # 模拟 AI 返回的结构化数据
    # 实际操作时，你需要将此 Prompt 发送给你的 LLM 接口
    return {
        "insight": "AI 生成的中文深度洞察...",
        "quotes": "Selected English quote 1...\nSelected English quote 2...",
        "lingo": "Strategic Pivot: 战略转型...",
        "question": "如果你现在的核心业务明天消失，你会..."
    }

def push_to_notion(data):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data['title']}}]},
            "Status": {"select": {"name": "Draft"}}, # 默认为草稿，供你筛选
            "Original_Text": {"rich_text": [{"text": {"content": data['quotes']}}]}, # 存放英文原文
            "Insight": {"rich_text": [{"text": {"content": data['insight']}}]}, # 存放中文洞察
            "Lingo": {"rich_text": [{"text": {"content": data['lingo']}}]},
            "Question": {"rich_text": [{"text": {"content": data['question']}}]}
        }
    }
    
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code

# 主逻辑
def run_sync():
    print("开始抓取全球管理动态...")
    # 这里接入你之前的抓取逻辑（RSS 或 网页爬虫）
    # 示例数据
    sample_article = {
        "title": "The Art of Strategic Patience",
        "content": "Full article text from HBR/McKinsey..."
    }
    
    analysis = get_ai_insight(sample_article['title'], sample_article['content'])
    status = push_to_notion({**sample_article, **analysis})
    
    if status == 200:
        print("✅ 深度内参已同步至 Notion！")
    else:
        print(f"❌ 同步失败，错误码: {status}")

if __name__ == "__main__":
    run_sync()
