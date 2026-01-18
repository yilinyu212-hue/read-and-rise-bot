import os, requests, feedparser

# 配置区
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

def run_task():
    # 1. 获取 Token
    t_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    token = requests.post(t_url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json().get("tenant_access_token")
    
    # 2. 抓取 RSS (以 HBR 为例)
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    for entry in feed.entries[:3]:
        # 3. 写入飞书 (严格匹配截图 ffe2639e 的表头)
        data = {
            "fields": {
                "培训主题": entry.title,
                "核心内容": entry.summary[:100] if hasattr(entry, 'summary') else "点击原文查看详情",
                "分类": "外刊",
                "链接": {"url": entry.link, "title": "阅读原文"}
            }
        }
        res = requests.post(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        ).json()
        print(f"同步结果: {res.get('msg')}")

if __name__ == "__main__":
    run_task()
