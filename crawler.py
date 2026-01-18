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
    """调用 DeepSeek 生成深度内容"""
    if not DEEPSEEK_API_KEY:
        print("⚠️ 警告：环境变量 DEEPSEEK_API_KEY 为空，请检查 GitHub Secrets 配置！")
        return "AI 配置缺失，请检查 GitHub Secrets。"

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    prompt = f"""
    作为一名教育者学术教练，请深度解析《{title}》(来源: {source_name})：
    
    1. 【核心摘要】: 250字中英文双语对照总结。
    2. 【双语词汇与句式】: 提取3个核心术语，1个高级句式。
    3. 【场景应用】: 教育领导者如何将此观点落地？
    4. 【苏格拉底反思流】: 设计3个引导思考的问题。
    5. 【实践案例】: 提供一个具体的应用实例。
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        # 使用 json= 参数会自动处理序列化，避免手动 dumps 导致的错误
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res_json = response.json()
        if "choices" in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            error_msg = res_json.get('error', {}).get('message', '未知错误')
            print(f"❌ DeepSeek 报错: {error_msg}")
            return f"AI 生成失败: {error_msg}"
    except Exception as e:
        print(f"⚠️ 网络请求异常: {e}")
        return "AI 内容生成中，请先阅读标题。"

def sync_to_feishu(token, title, link, source_name):
    print(f"🧠 正在分析: 《{title}》...")
    ai_content = ai_process_content(title, source_name)
    
    # --- [新增：强制在日志里打印前 100 个字，确认 AI 真的说话了] ---
    print(f"📝 AI 返回片段: {ai_content[:100]}...") 
    # -------------------------------------------------------

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    payload = {
        "fields": {
            "培训主题": title,
            "核心内容": ai_content,
            "分类": source_name,
            "链接": str(link)
        }
    }
    
    res_req = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload)
    res = res_req.json()
    
    if res.get("code") == 0:
        print(f"✅ 成功写入飞书！记录ID: {res.get('data', {}).get('record', {}).get('record_id')}")
        return True
    else:
        print(f"❌ 写入飞书失败: {res.get('msg')}")
        return False

def run():
    token = get_feishu_token()
    if not token: return
    for name, rss_url in SOURCES.items():
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                entry = feed.entries[0]
                if sync_to_feishu(token, entry.title, entry.link, name):
                    print(f"✅ {name} 同步成功")
        except Exception as e:
            print(f"⚠️ {name} 处理异常: {e}")

if __name__ == "__main__":
    run()
