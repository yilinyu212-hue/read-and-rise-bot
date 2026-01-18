import os, requests, feedparser, json

# 配置信息
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

SOURCES = {
    "HBR领导力": "https://hbr.org/rss/topic/leadership",
    "麦肯锡洞察": "https://www.mckinsey.com/insights/rss",
    "经济学人": "https://www.economist.com/business/rss.xml",
    "斯坦福教育": "https://news.stanford.edu/feed/"
}

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def ai_process_content(title, source_name):
    """调用 DeepSeek 按照 Read & Rise 的教育者视角生成内容"""
    if not DEEPSEEK_API_KEY:
        return "AI 配置缺失，请查看原文内容。"

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    prompt = f"""
    你是一位专门服务于教育者的专业译者和学术教练。
    请针对文章标题《{title}》(来源: {source_name}) 创作一份深度的学习笔记。
    
    要求如下：
    1. 【核心摘要】: 300字以内的中英文双语对照总结，语言要优雅、专业。
    2. 【双语词汇与句式】: 提取3个教育/商业核心术语，1个可在演讲中使用的金句。
    3. 【场景应用】: 作为一名教育领导者，如何将此文章的观点落地到学校或机构管理中？
    4. 【苏格拉底式反思流】: 设计3个层层递进的问题，引导读者进行批判性思考。
    5. 【教育者案例】: 虚构或引用一个简短案例来说明该观点的实际意义。
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=json.dumps(data)).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI 生成失败: {e}")
        return f"内容处理中，请先参考原标题：{title}"

def sync_to_feishu(token, title, link, source_name):
    print(f"🧠 正在为《{title}》生成 AI 深度解析...")
    ai_content = ai_process_content(title, source_name)
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    payload = {
        "fields": {
            "培训主题": title,
            "核心内容": ai_content, # 这里存入 AI 生成的长文本
            "分类": source_name,
            "链接": str(link)
        }
    }
    
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
    return res.get("code") == 0

def run():
    token = get_feishu_token()
    if not token: return
    
    for name, rss_url in SOURCES.items():
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                entry = feed.entries[0] # 每个源取最新一篇
                if sync_to_feishu(token, entry.title, entry.link, name):
                    print(f"✅ {name} 同步成功")
        except Exception as e:
            print(f"⚠️ {name} 处理异常: {e}")

if __name__ == "__main__":
    run()
