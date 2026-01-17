import os
import requests
import json

# --- 1. 配置环境（从 GitHub Secrets 读取） ---
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- 2. 核心函数：调用 DeepSeek 生成双语教练内容 ---
def ask_deepseek(name, category):
    url = "https://api.deepseek.com/chat/completions"
    
    # 🚨 这里的 Prompt 已经过“企业教练”逻辑调优
    prompt = f"""
    You are the Chief Executive Coach for "Read & Rise". 
    Target: {category} named "{name}".
    Please provide a bilingual (English & Chinese) deep analysis:

    1. [Original Title & Author]: List the full original English name and author.
    2. [Core Concept]: Identify 1 core English professional term (e.g., 'Radical Candor') with a deep Chinese explanation.
    3. [Executive Gold Quote]: One powerful quote in original English + precise Chinese translation.
    4. [Coaching Actionable]: 3 specific Chinese practical tips for leaders/educators.
    5. [Socratic Reflection]: One powerful Socratic question in both English and Chinese.

    Format the output elegantly with clear headings.
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a world-class Executive Coach proficient in English and Chinese."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    
    try:
        response = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, json=payload, timeout=60)
        res_data = response.json()
        if response.status_code == 200:
            return res_data['choices'][0]['message']['content']
        else:
            print(f"⚠️ DeepSeek Error: {res_data.get('error', {}).get('message')}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

# --- 3. 核心函数：连接 Notion 自动化 ---
def run_automation():
    # A. 查询 Status 为 "Pending" 的条目
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    query_data = {
        "filter": {
            "property": "Status",
            "select": {"equals": "Pending"}
        }
    }
    
    try:
        res = requests.post(query_url, headers=HEADERS, json=query_data).json()
        tasks = res.get("results", [])
    except Exception as e:
        print(f"❌ Failed to connect to Notion: {e}")
        return

    print(f"🚀 Found {len(tasks)} pending tasks.")

    for task in tasks:
        page_id = task["id"]
        # 获取书名/项目名
        title_list = task["properties"].get("Name", {}).get("title", [])
        if not title_list:
            continue
            
        name = title_list[0]["text"]["content"]
        cat = task["properties"].get("Category", {}).get("select", {}).get("name", "📖 Book")
        
        print(f"🔍 Processing: {name}...")
        
        # B. 调用 AI 生成内容
        content = ask_deepseek(name, cat)
        
        if content:
            # C. 将内容写回 Notion，并将状态改为 "Draft" (待审核)
            update_url = f"https://api.notion.com/v1/pages/{page_id}"
            update_data = {
                "properties": {
                    "Content_Payload": {
                        "rich_text": [{"text": {"content": content}}]
                    },
                    "Status": {
                        "select": {"name": "Draft"}
                    }
                }
            }
            patch_res = requests.patch(update_url, headers=HEADERS, json=update_data)
            if patch_res.status_code == 200:
                print(f"✅ Success: {name} is now in 'Draft' with AI content.")
            else:
                print(f"❌ Failed to update Notion: {patch_res.text}")

# --- 4. 运行入口 ---
if __name__ == "__main__":
    if not all([DEEPSEEK_KEY, NOTION_TOKEN, DATABASE_ID]):
        print("❌ Error: Missing API keys in Environment Variables.")
    else:
        run_automation()
