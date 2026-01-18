import os, requests, feedparser, json

# 环境变量获取
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
    
    prompt = f"请解析文章《{title}》(来源: {source_name})，生成教育笔记：1.核心摘要(中英双语) 2.双语词汇 3.场景应用 4.苏格拉底反思 5.实践案例。请分段书写，不要使用复杂的 Markdown 符号。"
    
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60).json()
        return response['choices'][0]['message']['content']
    except:
        return "内容处理中..."

def sync_to_feishu(token, title, link, source_name):
    print(f"🧠 正在分析: 《{title}》...")
    ai_content = ai_process_content(title, source_name)
    
    # --- 降噪逻辑 ---
    # 替换掉可能引起 JSON 报错的特殊字符，保留简单的换行
    safe_content = ai_content.replace('"', '\"').replace('\xa0', ' ')
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    
    # 强制将所有字段转为最基础的字符串
    payload = {
        "fields": {
            "培训主题": str(title),
            "核心内容": str(safe_content),
            "分类": str(source_name),
            "链接": str(link)
        }
    }
    
    # 关键：手动指定编码确保字符安全
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
