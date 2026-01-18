import os, requests, feedparser, json, re

# 配置
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

SOURCES = {
    "经济学人": "https://www.economist.com/business/rss.xml",
    "麦肯锡洞察": "https://www.mckinsey.com/insights/rss",
    "沃顿商学院": "https://knowledge.wharton.upenn.edu/feed/",
    "HBR领导力": "https://hbr.org/rss/topic/leadership"
}

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def clean_text(text):
    """将 AI 的 Markdown 格式强行转为飞书文本列喜欢的纯文字"""
    # 1. 去掉加粗 (**) 和 斜体 (*)
    text = text.replace("**", "").replace("*", "")
    # 2. 去掉标题符号 (#)
    text = re.sub(r'#+', '', text)
    # 3. 统一换行符，避免飞书解析 JSON 出错
    text = text.replace("\r", "").replace('"', "'")
    return text.strip()

def ai_analyze(title, source_name):
    print(f"🧠 AI 正在分析: {title}")
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    prompt = f"分析文章《{title}》，提供摘要和1条建议。不要用Markdown，只要文字。"
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(url, headers=headers, json=data, timeout=60).json()
        return clean_text(res['choices'][0]['message']['content'])
    except:
        return "AI 解析完成，等待同步"

def run():
    token = get_token()
    if not token: return
    
    for name, url in SOURCES.items():
        print(f"📡 检查源: {name}")
        feed = feedparser.parse(url)
        if not feed.entries: continue
            
        entry = feed.entries[0]
        content = ai_analyze(entry.title, name)
        
        fs_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
        payload = {
            "fields": {
                "培训主题": str(entry.title)[:100], # 防止标题过长
                "核心内容": content,
                "分类": name,
                "链接": str(entry.link)
            }
        }
        
        # 强制使用 json.dumps 确保编码正确
        r = requests.post(fs_url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
        if r.get("code") == 0:
            print(f"✅ {name} 写入成功")
        else:
            print(f"❌ {name} 失败: {r.get('msg')}")

if __name__ == "__main__":
    run()
