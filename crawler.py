import os, requests, feedparser, json

# 配置
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

SOURCES = {"HBR领导力": "https://hbr.org/rss/topic/leadership"}

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def ai_analyze(title):
    if not DEEPSEEK_API_KEY: return "AI Key Missing"
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    # 强制要求极短输出，测试是否为长度问题
    prompt = f"用100字总结文章《{title}》，不要换行，不要特殊字符。"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content'].replace('\n', ' ')
    except:
        return "AI analysis failed"

def sync():
    token = get_token()
    feed = feedparser.parse(SOURCES["HBR领导力"])
    if not feed.entries: return
    
    entry = feed.entries[0]
    title = entry.title
    link = entry.link
    content = ai_analyze(title)
    
    print(f"🧠 AI 结果: {content[:50]}...")

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    
    # 构造最简单的字段字典
    payload = {
        "fields": {
            "培训主题": str(title),
            "核心内容": str(content),
            "分类": "HBR",
            "链接": str(link)
        }
    }
    
    # 重点：打印完整的请求体，如果报错，你可以直接发给我
    print(f"📡 发送数据: {json.dumps(payload, ensure_ascii=False)}")
    
    response = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload)
    print(f"📩 飞书返回: {response.text}")

if __name__ == "__main__":
    sync()
