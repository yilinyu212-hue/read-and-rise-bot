import os
import requests
import feedparser
from datetime import datetime

# --- 1. 配置区 (已替换为你的飞书凭证) ---
DEEPSEEK_KEY = "sk-500a770ac8e74c4cb38286ba27164c4a"
APP_ID = "cli_a9e6e2fabcb8dcb2"
APP_SECRET = "6lqhEevwakrsPvEjknF4L8gM0BSGSmLI"
APP_TOKEN = "BNnhbUIMMaQFgKshPnKc7BEInwh"
TABLE_ID = "tblZHZLDmuMr7irX"

SOURCES = {
    "The Economist": "https://www.economist.com/finance-and-economics/rss.xml",
    "Harvard Business Review": "https://hbr.org/rss/topic/leadership",
    "McKinsey Insights": "https://www.mckinsey.com/insights/rss",
    "Fast Company": "https://www.fastcompany.com/leadership/rss",
    "Forbes Leadership": "https://www.forbes.com/leadership/feed/"
}

# --- 2. 获取飞书访问令牌 ---
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

# --- 3. 调用 AI 生成摘要 (让你的网页更有料) ---
def get_ai_summary(title):
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
        prompt = f"你是一位资深教育者。请为这篇文章标题写一段50字以内的中文导读，突出其对领导者的启发：{title}"
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except:
        return "内容正在深度解析中，稍后更新..."

# --- 4. 写入飞书多维表格 ---
def write_to_feishu(token, title, link, summary):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 注意：这里的字段名必须与你飞书表格里的列名完全一致
    data = {
        "fields": {
            "培训主题": title,
            "核心内容": summary,
            "分类": "外刊",
            "链接": {"url": link, "title": "阅读原文"},
            "时间": int(datetime.now().timestamp() * 1000)
        }
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res.get("code") == 0

# --- 5. 主运行逻辑 ---
def run_pipeline():
    print("📡 正在启动 Read & Rise 自动化爬虫...")
    token = get_feishu_token()
    if not token:
        print("❌ 飞书授权失败，请检查 Secret")
        return

    for source_name, url in SOURCES.items():
        print(f"🔎 正在扫描: {source_name}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]: # 每个源抓2篇最新的
            print(f"📖 发现文章: {entry.title}")
            
            # 这里的 AI 总结是关键，会让你的 ima 学习得更深入
            summary = get_ai_summary(entry.title)
            
            success = write_to_feishu(token, entry.title, entry.link, summary)
            if success:
                print(f"✅ 成功同步至飞书")
            else:
                print(f"⚠️ 同步失败，请检查表格字段名是否匹配")

if __name__ == "__main__":
    run_pipeline()
