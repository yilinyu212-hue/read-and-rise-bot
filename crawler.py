import os, requests, feedparser, json

# 配置
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 你的多源情报库 ---
SOURCES = {
    "HBR领导力": "https://hbr.org/rss/topic/leadership",
    "经济学人": "https://www.economist.com/business/rss.xml",
    "麦肯锡洞察": "https://www.mckinsey.com/insights/rss",
    "斯坦福教育": "https://news.stanford.edu/topic/education/feed/",
    "Edutopia创新": "https://www.edutopia.org/rss.xml",
    "沃顿商学院": "https://knowledge.wharton.upenn.edu/feed/"
}

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def ai_analyze(title, source_name):
    print(f"🧠 正在请求 AI 分析来自 [{source_name}] 的文章...")
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    prompt = f"作为教育者教练，请分析《{title}》(来源:{source_name})，提供摘要和3个苏格拉底式反思问题。纯文字格式。"
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(url, headers=headers, json=data, timeout=60).json()
        return res['choices'][0]['message']['content']
    except:
        return "AI 解析失败"

def run_all_sources():
    token = get_token()
    if not token: return
    
    for name, url in SOURCES.items():
        print(f"📡 正在检查源: {name}")
        feed = feedparser.parse(url)
        if not feed.entries:
            print(f"⚠️ {name} 暂时无更新")
            continue
            
        # 抓取每个源最新的第一篇
        entry = feed.entries[0]
        content = ai_analyze(entry.title, name)
        
        # 写入飞书
        fs_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
        payload = {
            "fields": {
                "培训主题": str(entry.title),
                "核心内容": str(content),
                "分类": name,
                "链接": str(entry.link)
            }
        }
        r = requests.post(fs_url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
        if r.get("code") == 0:
            print(f"✅ {name} 同步成功！")
        else:
            print(f"❌ {name} 写入失败: {r.get('msg')}")

if __name__ == "__main__":
    run_all_sources()
