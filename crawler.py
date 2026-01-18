import os
import requests
import feedparser

# 从 GitHub Secrets 读取环境变量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    try:
        res = requests.post(url, json=payload).json()
        return res.get("tenant_access_token")
    except:
        return None

def sync_to_feishu(token, title, link, summary):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 精准匹配飞书表头
    data = {
        "fields": {
            "培训主题": title,
            "核心内容": summary,
            "分类": "外刊",
            "链接": {"url": link, "title": "阅读原文"}
        }
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res.get("code") == 0

def run():
    print("🚀 开始执行 Read & Rise 爬虫任务...")
    token = get_feishu_token()
    if not token:
        print("❌ 授权失败，请检查 GitHub Secrets 中的 App ID 和 Secret")
        return

    # 抓取源：Harvard Business Review
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    for entry in feed.entries[:3]:
        summary = entry.summary[:150] + "..." if hasattr(entry, 'summary') else "最新领导力趋势，详见原文。"
        if sync_to_feishu(token, entry.title, entry.link, summary):
            print(f"✅ 成功同步: {entry.title}")
        else:
            print(f"❌ 同步失败: {entry.title}")

if __name__ == "__main__":
    run()
