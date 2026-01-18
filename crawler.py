import os, requests, feedparser, json

# 环境变量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def ai_analyze(title):
    if not DEEPSEEK_API_KEY: return "AI Key Missing"
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    # 告诉 AI 只要纯文本，不要任何奇怪的符号
    prompt = f"请简要总结文章《{title}》的核心观点，并提供一个给教育者的建议。要求：纯文字，不要星号，分段即可。"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=60).json()
        return res['choices'][0]['message']['content']
    except:
        return "AI 分析生成失败"

def sync():
    token = get_token()
    # 每次只抓取 HBR 的最新一篇来做测试，确保能通
    feed = feedparser.parse("https://hbr.org/rss/topic/leadership")
    if not feed.entries: return
    
    entry = feed.entries[0]
    content = ai_analyze(entry.title)
    
    print(f"🧠 AI 已生成内容，准备写入飞书...")
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    payload = {
        "fields": {
            "培训主题": str(entry.title),
            "核心内容": str(content),
            "分类": "HBR外刊",
            "链接": str(entry.link)
        }
    }
    
    # 打印飞书的真实反应
    response = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload)
    print(f"📩 飞书老师的批改意见: {response.text}")

if __name__ == "__main__":
    sync()
