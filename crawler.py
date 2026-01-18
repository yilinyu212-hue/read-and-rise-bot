import os
import requests
import feedparser

# 从 GitHub Secrets 读取新设的飞书变量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def write_to_feishu(token, title, link):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 严格匹配你的飞书列名：培训主题、核心内容、分类、链接
    data = {
        "fields": {
            "培训主题": title,
            "核心内容": "最新领导力资讯，详见原文链接。", # 这里之后可以加 DeepSeek 总结
            "分类": "外刊",
            "链接": {"url": link, "title": "阅读原文"}
        }
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res.get("code") == 0

def run():
    token = get_token()
    if not token: 
        print("❌ 授权失败，请检查 GitHub Secrets 中的 FEISHU_APP_SECRET")
        return
    
    # 抓取 HBR 领导力 RSS
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    for entry in feed.entries[:3]:
        if write_to_feishu(token, entry.title, entry.link):
            print(f"✅ 成功同步: {entry.title}")
        else:
            print(f"❌ 同步失败，请检查飞书列名是否匹配")

if __name__ == "__main__":
    run()
