import os, requests, feedparser

# 环境变量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

# 你的 8 个核心源
SOURCES = {
    "HBR领导力": "https://hbr.org/rss/topic/leadership",
    "麦肯锡洞察": "https://www.mckinsey.com/insights/rss",
    "经济学人": "https://www.economist.com/business/rss.xml",
    "MIT技术评论": "https://www.technologyreview.com/feed/",
    "Edutopia教育": "https://www.edutopia.org/rss.xml",
    "FastCompany": "https://www.fastcompany.com/latest/rss",
    "斯坦福教育": "https://news.stanford.edu/feed/",
    "世界经济论坛": "https://www.weforum.org/agenda/feed"
}

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def sync(token, title, link, source_name):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    
    # --- [关键修改：确保这里的 Key 和你飞书表格的列名一模一样] ---
    data = {
        "fields": {
            "培训主题": title, 
            "核心内容": f"来自 {source_name} 的最新洞察。AI 摘要生成中...",
            "分类": "外刊",
            "链接": {"url": link, "title": "阅读原文"}
        }
    }
    # --------------------------------------------------------
    
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=data).json()
    if res.get("code") != 0:
        print(f"❌ 同步失败原因: {res.get('msg')} (代码: {res.get('code')})")
        return False
    return True

def run():
    token = get_token()
    if not token: return
    print(f"🚀 开始多源同步任务...")
    for name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                entry = feed.entries[0]
                if sync(token, entry.title, entry.link, name):
                    print(f"✅ 成功同步: {name}")
        except Exception as e:
            print(f"⚠️ 源 {name} 连接超时")

if __name__ == "__main__":
    run()
