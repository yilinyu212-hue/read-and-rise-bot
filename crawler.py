import os
import requests
import json

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

def get_ai_analysis(title, content):
    # 模拟 AI 提炼逻辑，实际可接入 GPT-4 接口
    # 这里的 Prompt 强制要求了“原文摘录”
    return {
        "top_quote": "The greatest danger in times of turbulence is not the turbulence; it is to act with yesterday's logic.",
        "insight": "战略耐心与系统思考是应对波动的核心。本文强调了领导者不应只关注KPI，更要关注激励结构。",
        "models": ["系统思考", "原则"],
        "question": "你现在的决策逻辑，是在应对过去还是未来？"
    }

def push_to_notion(title, analysis):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 属性名需与 Notion 库完全一致
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Status": {"select": {"name": "Draft"}}, # 💡 默认为草稿，待专家审核
            "Top_Quote": {"rich_text": [{"text": {"content": analysis['top_quote']}}]},
            "Insight": {"rich_text": [{"text": {"content": analysis['insight']}}]},
            "Linked_Models": {"multi_select": [{"name": m} for m in analysis['models']]},
            "Reflective_Question": {"rich_text": [{"text": {"content": analysis['question']}}]}
        }
    }
    return requests.post(url, headers=headers, json=payload).status_code

if __name__ == "__main__":
    # 示例抓取流程
    title = "Navigating Strategic Ambiguity"
    analysis = get_ai_analysis(title, "Full content...")
    if push_to_notion(title, analysis) == 200:
        print("✅ 专家级内参已同步至 Notion (待审核状态)")
