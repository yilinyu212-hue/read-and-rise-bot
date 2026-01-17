import os
import requests

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

def ask_deepseek(name, category):
    # 🚨 这里的指令升级为：原版书名 + 中英教练解析
    prompt = f"你是一位企业教练。请针对原版书《{name}》（分类：{category}）生成深度双语解析，包含英文原句、中文洞察和苏格拉底提问。"
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    res = requests.post("https://api.deepseek.com/chat/completions", 
                        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, json=payload)
    return res.json()['choices'][0]['message']['content']

def run():
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(query_url, headers=headers, json={"filter": {"property": "Status", "select": {"equals": "Pending"}}})
    
    for task in res.json().get("results", []):
        page_id = task["id"]
        # 🚨 安全获取标题
        name = task["properties"]["Name"]["title"][0]["text"]["content"]
        # 🚨 安全获取分类（修复你遇到的 AttributeError）
        cat_obj = task["properties"].get("Category", {}).get("select")
        cat = cat_obj.get("name", "Book") if cat_obj else "Book"
        
        print(f"正在加工: {name}")
        content = ask_deepseek(name, cat)
        
        if content:
            requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json={
                "properties": {
                    "Content_Payload": {"rich_text": [{"text": {"content": content}}]},
                    "Status": {"select": {"name": "Draft"}}
                }
            })

if __name__ == "__main__":
    run()
