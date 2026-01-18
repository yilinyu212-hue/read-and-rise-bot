import os
import requests
import feedparser

# 从 GitHub Secrets 读取
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY") # 注意匹配你截图中的命名

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def write_to_feishu(token, title, link, summary):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 严格匹配飞书截图 的字段名
    data = {
        "fields": {
            "培训主题": title,
            "核心内容": summary,
            "分类": "外刊",
            "链接": {"url": link, "title": "点击阅读"}
        }
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res.get("code") == 0

def run():
    token = get_token()
    if not token: 
        print("❌ 无法获取飞书 Token，请检查 Secret 设置")
        return
    
    # 抓取 HBR 领导力 RSS
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    for entry in feed.entries[:3]:
        # 简单截取摘要
        summary = entry.summary[:100] if hasattr(entry, 'summary') else "最新领导力洞察，详见原文。"
        if write_to_feishu(token, entry.title, entry.link, summary):
            print(f"✅ 成功同步: {entry.title}")
        else:
            print(f"❌ 同步失败: {entry.title}")

if __name__ == "__main__":
    run()
