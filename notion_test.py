import os
import requests

# 确保 GitHub Secrets 中已设置这两个变量
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

def test_notion_connection():
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 极简 payload，测试 Name 字段
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": "📡 Read & Rise 链路通电测试成功！"}}]
            }
        }
    }
    
    print(f"正在测试... Token长度: {len(NOTION_TOKEN)}, ID前缀: {DATABASE_ID[:5]}")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ SUCCESS! 数据已写入 Notion。")
    else:
        print(f"❌ FAILED! 状态码: {response.status_code}")
        print(f"详细报错: {response.text}")

if __name__ == "__main__":
    test_notion_connection()
