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
    """调用 DeepSeek 生成深度内容"""
    if not DEEPSEEK_API_KEY: return "AI 配置缺失"
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    
    prompt = f"请解析文章《{title}》(来源: {source_name})，生成包含核心摘要、双语词汇、场景应用、苏格拉底反思流和实践案例的教育笔记。要求：排版清晰。"
    
    data = {
        "model": "deepseek-chat", 
        "messages": [{"role": "user", "content": prompt}], 
        "temperature": 0.5 # 降低随机性，减少乱码概率
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI 生成异常: {e}")
        return "内容处理中..."

def sync_to_feishu(token, title, link, source_name):
    print(f"🧠 正在分析: 《{title}》...")
    ai_content = ai_process_content(title, source_name)
    
    # --- 强力清洗逻辑：确保内容是纯文本字符串 ---
    # 1. 过滤掉可能导致 JSON 解析出错的非打印字符
    safe_content = "".join(c for c in str(ai_content) if c.isprintable() or c in '\n\r\t')
    # 2. 如果内容过长，截断至 15000 字（飞书多维表格文本列上限）
    safe_content = safe_content[:15000]
    
    print(f"📝 AI 返回片段: {safe_content[:50]}...")

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    
    # 构造请求数据。注意：'链接' 采用纯字符串格式以兼容文本列
    payload = {
        "fields": {
            "培训主题": str(title),
            "核心内容": safe_content,
            "分类": str(source_name),
            "链接": str(link)
        }
    }
    
    # 使用 json= 参数让 requests 库自动处理 Unicode 转义
    res_obj = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload)
    res = res_obj.json()
    
    if res.get("code") == 0:
        print(f"✅ 成功同步至飞书")
        return True
    else:
        print(f"❌ 飞书报错: {res.get('msg')} (代码: {res.get('code')})")
        # 调试信息：输出飞书预期的错误详情
        print(f"💡 字段详细错误: {res.get('error', {}).get('field_violations', '无具体字段违反记录')}")
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
