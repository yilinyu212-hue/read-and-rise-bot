import os
import requests
import json

# --- 1. 环境自检 ---
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

def check_env():
    if not DEEPSEEK_KEY:
        print("❌ 错误: DEEPSEEK_API_KEY 未设置！请检查 GitHub Secrets")
        return False
    if not NOTION_TOKEN or not DATABASE_ID:
        print("❌ 错误: Notion 相关变量未设置！")
        return False
    print(f"✅ 环境检查通过。DeepSeek Key 长度: {len(DEEPSEEK_KEY)}")
    return True

# --- 2. 核心 API 调用 ---
def ask_deepseek(target_name, category):
    """
    通过 DeepSeek 注入 Read & Rise 的教育灵魂
    """
    url = "https://api.deepseek.com/chat/completions"
    
    # 构建针对教育者视角的专业 Prompt
    prompt = f"""
    作为 Read & Rise 首席教育专家，请针对 {category}: 《{target_name}》进行深度建模：
    
    1. [Hi Leader]: 一句深入人心的开场白。
    2. [Top_Quote]: 1句最有穿透力的英文原文。
    3. [Mental_Model]: 提炼 1 个核心思维模型（包含模型名和深度逻辑）。
    4. [Case_Insight]: 简述 1 个相关的全球商业案例。
    5. [Socratic_Question]: 1 个直击灵魂的苏格拉底式提问。
    """
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位拥有全球视野的管理学教育家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        res_data = response.json()
        
        if response.status_code == 200:
            return res_data['choices'][0]['message']['content']
        else:
            print(f"❌ DeepSeek 返回错误: {response.status_code}")
            print(f"响应详情: {json.dumps(res_data, indent=2)}")
            return None
    except Exception as e:
        print(f"❌ 网络请求异常: {str(e)}")
        return None

# --- 3. Notion 读写逻辑 ---
def get_pending_tasks():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    # 过滤 Status 为 Pending 的任务
    payload = {
        "filter": {
            "property": "Status",
            "select": {"equals": "Pending"}
        }
    }
    res = requests.post(url, headers=headers, json=payload).json()
    return res.get("results", [])

def update_notion_page(page_id, ai_content):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    # 将 AI 生成的内容填入 Content_Payload，并将状态改为 Draft
    payload = {
        "properties": {
            "Content_Payload": {
                "rich_text": [{"text": {"content": ai_content}}]
            },
            "Status": {
                "select": {"name": "Draft"}
            }
        }
    }
    res = requests.patch(url, headers=headers, json=payload)
    return res.status_code

# --- 4. 主运行程序 ---
if __name__ == "__main__":
    if check_env():
        tasks = get_pending_tasks()
        print(f"📢 发现 {len(tasks)} 条待处理任务")
        
        for task in tasks:
            page_id = task["id"]
            # 提取 Notion 中的标题和类别
            try:
                name = task["properties"]["Name"]["title"][0]["text"]["content"]
                # 检查 Category 是否已选，未选则默认 Book
                cat_data = task["properties"].get("Category", {}).get("select")
                cat = cat_data["name"] if cat_data else "📖 Book"
                
                print(f"正在处理: [{cat}] {name} ...")
                ai_result = ask_deepseek(name, cat)
                
                if ai_result:
                    status = update_notion_page(page_id, ai_result)
                    if status == 200:
                        print(f"✅ {name} 提炼成功并存入 Notion！")
                    else:
                        print(f"❌ Notion 更新失败，错误码: {status}")
                else:
                    print(f"⚠️ {name} 的 AI 生成失败，跳过。")
            except Exception as e:
                print(f"❌ 处理单条数据时出错: {e}")
