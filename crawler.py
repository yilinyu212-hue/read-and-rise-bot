import os, requests, feedparser, json

# 配置环境变量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

SOURCES = {"HBR领导力": "https://hbr.org/rss/topic/leadership"}

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def ai_process_content(title):
    if not DEEPSEEK_API_KEY: return "AI Key Missing"
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    
    # 稍微缩减篇幅，确保第一次尝试能成功写入
    prompt = f"分析文章《{title}》，生成：1.摘要 2.词汇 3.反思。请用纯文字，不要符号。"
    
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 错误: {str(e)}"

def sync_to_feishu():
    token = get_feishu_token()
    feed = feedparser.parse(SOURCES["HBR领导力"])
    if not feed.entries: return
    
    entry = feed.entries[0]
    ai_content = ai_process_content(entry.title)
    
    # --- 核心改进：飞书标准 JSON 写入格式 ---
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    
    payload = {
        "fields": {
            "培训主题": str(entry.title),
            "核心内容": str(ai_content).replace('"', "'"), # 避免引号嵌套冲突
            "分类": "HBR",
            "链接": str(entry.link)
        }
    }
    
    print(f"📡 尝试写入: {entry.title}")
    res_obj = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload)
    print(f"📩 飞书响应原文: {res_obj.text}")

if __name__ == "__main__":
    sync_to_feishu()
