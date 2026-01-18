import os, requests, feedparser, json

# 配置（从环境变量读取）
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
    """调用 DeepSeek 生成内容"""
    if not DEEPSEEK_API_KEY: return "AI 配置缺失"
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    prompt = f"请解析文章《{title}》(来源: {source_name})，生成包含核心摘要、双语词汇、场景应用、苏格拉底反思流和实践案例的教育笔记。请用清晰的Markdown格式。"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60).json()
        return response['choices'][0]['message']['content']
    except:
        return "AI 解析生成中..."

def sync_to_feishu(token, title, link, source_name):
    print(f"🧠 正在分析: 《{title}》...")
    ai_content = ai_process_content(title, source_name)
    
    # --- 关键修复：清洗文本，防止 WrongRequestBody ---
    # 确保内容是纯字符串，并移除可能导致 JSON 解析错误的极其罕见字符
    safe_content = str(ai_content).replace('\ufffd', '') 
    print(f"📝 AI 返回片段: {safe_content[:50]}...")

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    
    # 构造标准飞书请求体
    payload = {
        "fields": {
            "培训主题": str(title),
            "核心内容": safe_content,
            "分类": str(source_name),
            "链接": str(link)
        }
    }
    
    # 使用 json= 自动处理所有转义
    res = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
    
    if res.get("code") == 0:
        print(f"✅ 成功同步至飞书")
        return True
    else:
        print(f"❌ 飞书报错: {res.get('msg')} (代码: {res.get('code')})")
        # 调试用：如果还报错，打印出发送的字段名，核对是否匹配
        print(f"🔍 当前尝试写入的字段名: {list(payload['fields'].keys())}")
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
