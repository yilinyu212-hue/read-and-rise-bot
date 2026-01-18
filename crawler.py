import os, requests, feedparser, json

# 环境变量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

SOURCES = {"HBR领导力": "https://hbr.org/rss/topic/leadership", "麦肯锡洞察": "https://www.mckinsey.com/insights/rss"}

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def ai_analyze(title):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    # 恢复 Markdown 格式，为了后续在网页和飞书里更好看
    prompt = f"深度解析《{title}》。格式要求：### 摘要\n(内容)\n\n### 苏格拉底反思\n- (问题1)"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
    res = requests.post(url, headers=headers, json=data).json()
    return res['choices'][0]['message']['content']

def run():
    token = get_token()
    all_articles = []

    for name, url in SOURCES.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        content = ai_analyze(entry.title)

        # --- 步骤 1: 存入本地 data.json (驱动网页排版) ---
        all_articles.append({
            "title": entry.title,
            "content": content,
            "source": name,
            "link": entry.link
        })

        # --- 步骤 2: 同步到飞书知识库 (沉淀与检索) ---
        fs_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
        payload = {"fields": {"培训主题": str(entry.title), "核心内容": str(content), "分类": name, "链接": str(entry.link)}}
        requests.post(fs_url, headers={"Authorization": f"Bearer {token}"}, json=payload)

    # 保存到本地文件
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print("✅ 网页数据与飞书知识库已同步更新")

if __name__ == "__main__":
    run()
