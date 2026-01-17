import os
import requests
import json

# 配置环境变量
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_pending_tasks():
    """找到 Notion 中 Status 为 Pending 的条目"""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Status",
            "select": {"equals": "Pending"}
        }
    }
    res = requests.post(url, headers=HEADERS, json=payload).json()
    return res.get("results", [])

def ask_deepseek(target_name, category):
    """调用 DeepSeek 生成专家级内容"""
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""
    作为 Read & Rise 首席教育专家，请针对{category}: 《{target_name}》进行深度解析。
    输出格式要求：
    1. [Hi Leader]: 一句深入人心的开场白。
    2. [Top_Quote]: 1句最有穿透力的英文原文。
    3. [Mental_Model]: 1个核心思维模型（包含模型名和深度逻辑）。
    4. [Socratic_Question]: 1个扎心的反思提问。
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, json=data).json()
    return res['choices'][0]['message']['content']

def update_notion_page(page_id, content):
    """将 AI 生成的内容写回 Notion 并更新状态"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Content_Payload": {"rich_text": [{"text": {"content": content}}]},
            "Status": {"select": {"name": "Draft"}}
        }
    }
    requests.patch(url, headers=HEADERS, json=payload)

if __name__ == "__main__":
    tasks = get_pending_tasks()
    for task in tasks:
        page_id = task["id"]
        name = task["properties"]["Name"]["title"][0]["text"]["content"]
        cat = task["properties"]["Category"]["select"]["name"]
        
        print(f"正在为 {name} 生成内容...")
        ai_content = ask_deepseek(name, cat)
        update_notion_page(page_id, ai_content)
        print(f"✅ {name} 处理完成")
