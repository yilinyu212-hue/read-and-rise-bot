import os, requests, feedparser

# 环境变量 (保持不变)
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

# 5-8个精选源
SOURCES = {
    "HBR领导力": "https://hbr.org/rss/topic/leadership",
    "麦肯锡全球洞察": "https://www.mckinsey.com/insights/rss",
    "经济学人商业": "https://www.economist.com/business/rss.xml",
    "MIT技术评论": "https://www.technologyreview.com/feed/",
    "Edutopia创新教育": "https://www.edutopia.org/rss.xml",
    "FastCompany创新": "https://www.fastcompany.com/latest/rss",
    "斯坦福教育": "https://news.stanford.edu/feed/",
    "世界经济论坛": "https://www.weforum.org/agenda/feed"
}

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def sync(token, title, link, source_name):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    data = {
        "fields": {
            "培训主题": title,
            "核心内容": f"来源: {source_name}。最新全球前沿资讯，点击原文深度阅读。",
            "分类": "外刊",
            "链接": {"url": link, "title": "阅读原文"}
        }
    }
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=data).json()
    return res.get("code") == 0

def run():
    token = get_token()
    if not token: return
    
    print(f"🚀 开始多源抓取任务...")
    for name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            # 每个源只取最新的一篇，防止瞬间塞满表格
            if feed.entries:
                entry = feed.entries[0]
                if sync(token, entry.title, entry.link, name):
                    print(f"✅ 成功从 [{name}] 同步: {entry.title}")
                else:
                    print(f"❌ [{name}] 同步失败，请检查飞书列名")
        except Exception as e:
            print(f"⚠️ 无法连接到源 [{name}]: {e}")

if __name__ == "__main__":
    run()
