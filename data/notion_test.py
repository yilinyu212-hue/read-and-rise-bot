import os, requests

# 获取环境变量
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()

def test():
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    # 极简 Payload：只传一个 Name 字段
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": "🎉 链路测试：如果你看到这行字，说明通了！" }}]}
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        print("✅ 成功！请刷新 Notion 页面查看。")
    else:
        print(f"❌ 失败！错误信息：{res.text}")

if __name__ == "__main__":
    test()
