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
    "斯坦福教育": "https://news.stanford.edu/feed/"
}

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def sync(token, title, link, source_name):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    
    # 既然超链接对象报错，我们改用“纯文本推送”模式
    # 飞书的超链接列通常也兼容直接推送 URL 字符串
    payload = {
        "fields": {
            "培训主题": str(title),
            "核心内容": f"来源: {source_name}。全球前沿资讯同步。",
            "分类": "外刊",
            "链接": str(link)  # <--- 这里改成最简单的字符串格式
        }
    }
    
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
    
    if res.get("code") == 0:
        return True
    else:
        # 如果还是不行，我们将看到飞书返回的最新错误原因
        print(f"❌ 尝试失败! 错误信息: {res.get('msg')} (代码: {res.get('code')})")
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
