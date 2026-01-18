import os, requests, feedparser

# 环境变量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

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
    
    # 方案 A: 飞书标准超链接对象格式
    payload_a = {
        "fields": {
            "培训主题": title,
            "核心内容": f"来自 {source_name} 的最新洞察。AI 摘要同步中...",
            "分类": "外刊",
            "链接": {"url": link, "title": "阅读原文"}
        }
    }
    
    # 方案 B: 纯文本格式 (有时飞书列类型看似是超链接，但API只收文本)
    payload_b = {
        "fields": {
            "培训主题": title,
            "核心内容": f"来自 {source_name} 的最新洞察。AI 摘要同步中...",
            "分类": "外刊",
            "链接": link
        }
    }

    # 先试方案 A
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload_a).json()
    if res.get("code") == 0:
        return True
    
    # A 不行再试 B
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload_b).json()
    if res.get("code") == 0:
        return True
    
    print(f"❌ 全部格式转换失败: {res.get('msg')} (代码: {res.get('code')})")
    return False

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
            print(f"⚠️ 源 {name} 异常: {e}")

if __name__ == "__main__":
    run()
