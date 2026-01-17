import requests

# 🚨 暂时直接写死在这里，排除 GitHub Secrets 没读取到的可能
NOTION_TOKEN = "你的secret_开头的那串完整Token"
DATABASE_ID = "2e9e1ae7843a80ce8fe1f187a5adda68" # 确保只有这32位

def test():
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": "💪 最后的暴力测试：如果还不通我就改姓" }}]}
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"状态码: {res.status_code}")
    print(f"响应内容: {res.text}")

if __name__ == "__main__":
    test()
