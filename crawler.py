import os, requests, feedparser, json

# 从 GitHub Secrets 获取配置
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 订阅源
SOURCES = {
    "HBR领导力": "https://hbr.org/rss/topic/leadership",
    "麦肯锡洞察": "https://www.mckinsey.com/insights/rss",
    "经济学人": "https://www.economist.com/business/rss.xml",
    "斯坦福教育": "https://news.stanford.edu/feed/"
}

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
        return res.get("tenant_access_token")
    except Exception as e:
        print(f"❌ 获取飞书 Token 失败: {e}")
        return None

def ai_process_content(title, source_name):
    """调用 DeepSeek 按照 Read & Rise 的教育者视角生成深度内容"""
    if not DEEPSEEK_API_KEY:
        return "⚠️ AI 配置缺失，请在 GitHub Secrets 中检查 DEEPSEEK_API_KEY。"

    # DeepSeek 标准 API 终结点
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    prompt = f"""
    你是一位专门服务于教育者的专业译者和学术教练。
    请针对文章标题《{title}》(来源: {source_name}) 创作一份深度的学习笔记。
    
    要求如下：
    1. 【核心摘要】: 300字以内的中英文双语对照总结。
    2. 【双语词汇与句式】: 提取3个核心术语，1个可在演讲中使用的金句。
    3. 【场景应用】: 作为教育领导者，如何将此观点落地？
    4. 【苏格拉底反思流】: 设计3个层层递进的问题引导批判性思考。
    5. 【教育者案例】: 引用一个简短案例来说明。
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        # 修正请求逻辑：使用 json=参数会自动处理序列化
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res_json = response.json()
        if "choices" in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            print(f"❌ AI 报错详情: {res_json}")
            return "AI 内容生成暂存异常，请稍后刷新。"
    except Exception as e:
        print(f"⚠️ AI 请求发生错误: {e}")
        return "内容处理中，请参考原文链接。"

def sync_to_feishu(token, title, link, source_name):
    print(f"🧠 正在分析: 《{title}》...")
    ai_content = ai_process_content(title, source_name)
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    payload = {
        "fields": {
            "培训主题": title,
            "核心内容": ai_content,
            "分类": source_name,
            "链接": str(link)
        }
    }
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
        return res.get("code") == 0
    except Exception as e:
        print(f"❌ 写入飞书失败: {e}")
        return False

def run():
    token = get_feishu_token()
    if not token: return
    
    print(f"🚀 Read & Rise 自动化任务启动...")
    for name, rss_url in SOURCES.items():
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                entry = feed.entries[0]
                if sync_to_feishu(token, entry.title, entry.link, name):
                    print(f"✅ {name} 同步成功")
                else:
                    print(f"❌ {name} 同步失败，请检查飞书字段名。")
        except Exception as e:
            print(f"⚠️ {name} 处理异常: {e}")

if __name__ == "__main__":
    run()
