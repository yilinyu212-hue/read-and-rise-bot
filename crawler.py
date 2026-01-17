import os
import requests
import json

# 环境获取
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def ask_deepseek(name, category):
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""
    作为 Read & Rise 首席教育专家，请针对{category}《{name}》进行深度建模：
    1. [Hi_Leader]: 一句深入人心的教育者寄语。
    2. [Top_Quote]: 1句最有穿透力的英文原文。
    3. [Mental_Model]: 提炼1个核心思维模型（包含模型名和深度逻辑）。
    4. [Socratic_Question]: 1个扎心的苏格拉底式提问。
    """
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位拥有全球视野的管理学教育家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ AI 生成失败: {e}")
        return None

def run_automation():
    # 1. 查找待处理任务
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    query_data = {"filter": {"property": "Status", "select": {"equals": "Pending"}}}
    tasks = requests.post(query_url, headers=HEADERS, json=query_data).json().get("results", [])
    
    print(f"发现 {len(tasks)} 条新任务")
    
    for task in tasks:
        page_id = task["id"]
        name = task["properties"]["Name"]["title"][0]["text"]["content"]
        cat = task["properties"].get("Category", {}).get("select", {}).get("name", "📖 Book")
        
        print(f"正在加工: {name}...")
        content = ask_deepseek(name, cat)
        
        if content:
            # 2. 写回 Notion 并设为 Draft
            update_url = f"https://api.notion.com/v1/pages/{page_id}"
            update_data = {
                "properties": {
                    "Content_Payload": {"rich_text": [{"text": {"content": content}}]},
                    "Status": {"select": {"name": "Draft"}}
                }
            }
            requests.patch(update_url, headers=HEADERS, json=update_data)
            print(f"✅ {name} 已存入 Notion")

if __name__ == "__main__":
    if DEEPSEEK_KEY:
        run_automation()
    else:
        print("❌ 缺少 API Key，请检查 Secrets 配置")
