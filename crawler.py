import os, requests, feedparser, json, re
from datetime import datetime

# 1. 基础配置（请确保 GitHub Secrets 中已配置这些变量）
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 2. 你的全球教育情报源
SOURCES = {
    "HBR领导力": "https://hbr.org/rss/topic/leadership",
    "经济学人": "https://www.economist.com/business/rss.xml",
    "麦肯锡洞察": "https://www.mckinsey.com/insights/rss",
    "斯坦福教育": "https://news.stanford.edu/topic/education/feed/",
    "Edutopia创新": "https://www.edutopia.org/rss.xml"
}

def get_feishu_token():
    """获取飞书访问凭证"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
        return res.get("tenant_access_token")
    except:
        return None

def ai_analyze(title, source_name):
    # ... 前面的代码保持不变 ...
    prompt = f"""
    作为 AI Business Coach，请深度拆解《{title}》。
    除了文字分析，请根据内容对以下 5 个领导力维度进行评分 (0-100)：
    1. 战略思维 (Strategic Thinking)
    2. 组织进化 (Organizational Evolution)
    3. 决策韧性 (Decision Resilience)
    4. 行业洞察 (Industry Insight)
    5. 技术视野 (Tech Vision)

    请严格按照以下 JSON 格式输出，不要有其他废话：
    {{
      "analysis": "这里填写你的深度分析文字...",
      "scores": {{
        "战略思维": 80,
        "组织进化": 70,
        "决策韧性": 60,
        "行业洞察": 90,
        "技术视野": 85
      }}
    }}
    """
    # ... 发送请求并解析返回的 JSON ...

def run_sync():
    token = get_feishu_token()
    all_articles = []
    
    # 如果本地已有数据，先加载（用于网页显示最近内容）
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                all_articles = json.load(f)
        except:
            all_articles = []

    for name, rss_url in SOURCES.items():
        print(f"📡 正在检查源: {name}")
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            continue
            
        # 抓取每个源最新的第一篇
        entry = feed.entries[0]
        
        # 检查是否已经是处理过的文章（避免重复分析）
        if any(item['title'] == entry.title for item in all_articles):
            print(f"⏭️ 《{entry.title}》已存在，跳过。")
            continue

        # AI 解析
        content = ai_analyze(entry.title, name)
        
        # 准备存入的数据包
        article_data = {
            "title": entry.title,
            "content": content,
            "source": name,
            "link": entry.link,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # --- 步骤 A: 准备写入网页本地缓存 ---
        all_articles.insert(0, article_data)

        # --- 步骤 B: 同步到飞书知识库 (Bitable) ---
        if token:
            fs_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
            # 极限清洗，防止 WrongRequestBody 报错
            safe_content = content.replace('"', "'")
            payload = {
                "fields": {
                    "培训主题": str(entry.title),
                    "核心内容": str(safe_content),
                    "分类": name,
                    "链接": str(entry.link)
                }
            }
            res = requests.post(fs_url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
            if res.get("code") == 0:
                print(f"✅ 飞书知识库同步成功: {name}")
            else:
                print(f"⚠️ 飞书同步失败但已保存本地: {res.get('msg')}")

    # 保存最近 20 条到本地 data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_articles[:20], f, ensure_ascii=False, indent=4)
    print("🏁 任务运行结束，网页与飞书均已更新。")

if __name__ == "__main__":
    run_sync()
