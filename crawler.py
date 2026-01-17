import os
import requests

# 从环境变量读取 Key
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

def ask_deepseek(name, category):
    # 针对教练身份优化的双语 Prompt
    prompt = f"你是一位拥有哈佛商学院背景的企业教练。请针对《{name}》（类别：{category}）生成深度双语解析。包含：1.英文原版概念；2.中文实操洞察；3.中英对照的苏格拉底式提问。"
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a bilingual executive coach."}, {"role": "user", "content": prompt}]
    }
    res = requests.post("https://api.deepseek.com/chat/completions", 
                        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, json=payload)
    return res.json()['choices'][0]['message']['content']

def run():
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(query_url, headers=headers, json={"filter": {"property": "Status", "select": {"equals": "Pending"}}})
    
    results = res.json().get("results", [])
    print(f"🚀 找到 {len(results)} 个待处理任务")

    for task in results:
        page_id = task["id"]
        # 获取标题
        title_list = task["properties"].get("Name", {}).get("title", [])
        name = title_list[0]["text"]["content"] if title_list else "Unknown"
        
        # --- 🛡️ 防崩补丁：如果 Category 为空，默认赋值为 "Book" ---
        cat_obj = task["properties"].get("Category", {}).get("select")
        cat = cat_obj.get("name", "Book") if cat_obj else "Book"
        
        print(f"🔍 正在解析: {name}")
        content = ask_deepseek(name, cat)
        
        if content:
            requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json={
                "properties": {
                    "Content_Payload": {"rich_text": [{"text": {"content": content}}]},
                    "Status": {"select": {"name": "Draft"}}
                }
            })
            print(f"✅ {name} 已存入 Draft")

if __name__ == "__main__":
    run()
