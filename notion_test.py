import os, requests

# 自动从你之前设置的 Secrets 里读取
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

def test():
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    # 极简测试：只发一个标题
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": "📡 Read & Rise 链路测试成功！" }}]}
        }
    }
    print(f"正在尝试连接 Notion，Database ID: {DATABASE_ID[:5]}...")
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        print("✅ 成功！请去 Notion 页面刷新查看是否有新行。")
    else:
        print(f"❌ 失败！报错码: {res.status_code}, 报错信息: {res.text}")

if __name__ == "__main__":
    test()
