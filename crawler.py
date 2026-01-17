import os, requests

# --- 环境配置 ---
def run_ai_coach():
    DEEPSEEK_KEY = "sk-500a770ac8e74c4cb38286ba27164c4a"
    NOTION_TOKEN = "ntn_6058092242690eiABGM9YMvb0HPUXg9K40aFAfe1H59CV"
    DATABASE_ID = "2e9e1ae7843a80ce8fe1f187a5adda68"

    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    # 获取待处理任务
    res = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", 
                        headers=headers, json={"filter": {"property": "Status", "select": {"equals": "Pending"}}})
    
    for task in res.json().get("results", []):
        page_id = task["id"]
        name = task["properties"]["Name"]["title"][0]["text"]["content"]
        cat_obj = task["properties"].get("Category", {}).get("select")
        cat = cat_obj.get("name", "📖 Original Book") if cat_obj else "📖 Original Book"
        
        print(f"🚀 AI 教练正在深度研读: {name}...")

        # 针对教练身份量身定制的 Prompt
        prompt = f"""
        作为 Read & Rise 首席教练，请针对{cat}《{name}》进行双语解析。
        要求如下：
        1. [Bilingual Concept]: 提取1个核心英文原版术语，并进行中文深度解析。
        2. [Elite Quote]: 1句原版英文金句 + 专家级中文翻译。
        3. [Coaching Actionable]: 给出3条针对中国企业管理者或教育者的实操建议。
        4. [Socratic Question]: 1个中英对照的苏格拉底式提问，引发深度思考。
        
        请使用专业、优雅、有穿透力的语调。
        """

        # 调用 DeepSeek
        ai_res = requests.post("https://api.deepseek.com/chat/completions", 
                              headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
                              json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
        
        content = ai_res.json()['choices'][0]['message']['content']
        
        # 回写 Notion
        requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json={
            "properties": {
                "Content_Payload": {"rich_text": [{"text": {"content": content}}]},
                "Status": {"select": {"name": "Draft"}}
            }
        })
        print(f"✅ {name} 解析完成，已存入 Draft。")

if __name__ == "__main__":
    run_ai_coach()
