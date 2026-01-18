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
    
    # 终极尝试：直接发送最纯粹的链接对象
    # 很多时候是因为 title 包含特殊字符导致转换失败，我们这次只发 URL
    payload = {
        "fields": {
            "培训主题": title,
            "核心内容": f"来源: {source_name}。全球前沿资讯同步。",
            "分类": "外刊",
            "链接": {"url": link} 
        }
    }
    
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
    
    if res.get("code") == 0:
        return True
    else:
        # 如果还是不行，打印最详细的报错，方便我们对症下药
        print(f"❌ 尝试失败! 错误信息: {res.get('msg')} (代码: {res.get('code')})")
        print(f"💡 建议检查飞书表格中 ['链接'] 这一列的列名是否有空格，或类型是否正确。")
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
