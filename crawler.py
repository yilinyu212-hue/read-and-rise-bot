import os, requests, feedparser, json

# 环境变量
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
    if not DEEPSEEK_API_KEY: return "AI 配置缺失"
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    # 强制 AI 不要输出任何 Markdown 符号，只用空格和换行
    prompt = f"分析文章《{title}》(来源: {source_name})，生成包含摘要、词汇、应用、反思的笔记。要求：纯文字，不要使用星号或井号等符号。"
    
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60).json()
        return response['choices'][0]['message']['content']
    except:
        return "内容处理中..."

def sync_to_feishu(token, title, link, source_name):
    print(f"🧠 正在分析: 《{title}》...")
    ai_content = ai_process_content(title, source_name)
    
    # 极限脱敏：移除所有可能引起飞书报错的控制字符
    clean_content = "".join(c for c in ai_content if c.isprintable() or c == '\n')
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    payload = {
        "fields": {
            "培训主题": str(title),
            "核心内容": str(clean_content),
            "分类": str(source_name),
            "链接": str(link)
        }
    }
    
    # 使用 json= 参数确保所有转义由库自动完成
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
    
    if res.get("code") == 0:
        print(f"✅ 成功同步至飞书")
        return True
    else:
        print(f"❌ 飞书报错: {res.get('msg')} (代码: {res.get('code')})")
        return False

def run():
    token = get_feishu_token()
    if not token: return
    for name, rss_url in SOURCES.items():
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                if sync_to_feishu(token, feed.entries[0].title, feed.entries[0].link, name):
                    print(f"🎉 {name} 任务完成")
        except Exception as e:
            print(f"⚠️ 异常: {e}")

if __name__ == "__main__":
    run()
