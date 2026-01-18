import os
import requests
import feedparser
from datetime import datetime

# 从 GitHub Secrets 获取配置
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

SOURCES = {
    "The Economist": "https://www.economist.com/finance-and-economics/rss.xml",
    "Harvard Business Review": "https://hbr.org/rss/topic/leadership"
}

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

def get_ai_summary(title):
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": f"请为这篇文章写一段30字左右的中文领导力启示：{title}"}]
        }
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except:
        return "AI 正在深度解析中..."

def write_to_feishu(token, title, link, summary):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 【精准对齐】根据你的截图 ffe2639e
    data = {
        "fields": {
            "培训主题": title,      # 匹配截图第一列
            "核心内容": summary,    # 匹配截图第二列
            "分类": "外刊",        # 匹配截图第三列
            "链接": link           # 匹配截图第四列（如果报错，请尝试 {"url": link}）
        }
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res.get("code") == 0

def run():
    token = get_feishu_token()
    if not token: return
    for name, url in SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            summary = get_ai_summary(entry.title)
            success = write_to_feishu(token, entry.title, entry.link, summary)
            print(f"{'✅' if success else '❌'} 同步: {entry.title}")

if __name__ == "__main__":
    run()
