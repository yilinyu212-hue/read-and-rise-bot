import os, requests, feedparser, json

# 配置信息
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def run_task():
    print("🚀 步骤 1: 开始运行爬虫...")
    
    # 获取 Token
    t_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(t_url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    token = res.get("tenant_access_token")
    if not token:
        print("❌ 错误: 无法获取飞书 Token，请检查 APP_ID 和 SECRET")
        return
    print("✅ 步骤 2: 飞书授权成功")

    # 抓取 RSS
    feed_url = "https://hbr.org/rss/topic/leadership"
    print(f"📡 步骤 3: 正在尝试抓取源: {feed_url}")
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        print("⚠️ 提示: RSS 源目前没有文章，任务停止。")
        return
    
    entry = feed.entries[0]
    print(f"📄 找到文章: 《{entry.title}》")

    # AI 分析
    print("🧠 步骤 4: 正在请求 DeepSeek AI 进行深度解析 (预计耗时 1 分钟)...")
    ai_url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    prompt = f"分析文章《{entry.title}》，生成：1.摘要 2.教育者应用建议 3.苏格拉底反思。纯文字格式。"
    
    try:
        ai_res = requests.post(ai_url, headers=headers, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }, timeout=120).json()
        content = ai_res['choices'][0]['message']['content']
        print("✅ 步骤 5: AI 内容生成完毕！")
    except Exception as e:
        print(f"❌ AI 步骤失败: {e}")
        return

    # 写入飞书
    print("💾 步骤 6: 正在将内容写入飞书多维表格...")
    fs_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    payload = {
        "fields": {
            "培训主题": str(entry.title),
            "核心内容": str(content),
            "分类": "HBR实战",
            "链接": str(entry.link)
        }
    }
    
    final_res = requests.post(fs_url, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
    
    if final_res.get("code") == 0:
        print("🎉 恭喜！数据已成功存入飞书。")
    else:
        print(f"❌ 飞书保存失败! 错误码: {final_res.get('code')}, 信息: {final_res.get('msg')}")
        print(f"🔍 调试信息: {final_res.get('error', {})}")

if __name__ == "__main__":
    run_task()
