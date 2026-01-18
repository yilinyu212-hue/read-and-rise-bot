import os, requests, feedparser

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

def run():
    print("🚀 开始执行 Read & Rise 爬虫任务...")
    t_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    token = requests.post(t_url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json().get("tenant_access_token")
    
    if not token:
        print("❌ 飞书授权失败")
        return

    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    for entry in feed.entries[:3]:
        data = {
            "fields": {
                "培训主题": entry.title,
                "核心内容": entry.summary[:150] if hasattr(entry, 'summary') else "点击原文查看详情",
                "分类": "外刊",
                "链接": {"url": entry.link, "title": "阅读原文"}
            }
        }
        res = requests.post(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        ).json()
        print(f"{'✅' if res.get('code')==0 else '❌'} 同步: {entry.title}")

if __name__ == "__main__":
    run()
