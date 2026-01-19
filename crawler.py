import requests, feedparser, json, os
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# ================= 引擎 1：爬虫快报逻辑 =================
def fetch_rss_briefs():
    sources = [{"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"}] # 此处添加你那12个源
    briefs = []
    for s in sources:
        try:
            feed = feedparser.parse(s['url'])
            for item in feed.entries[:2]: # 每个源只取2条，保证响应速度
                briefs.append({"title": item.title, "link": item.link, "source": s['name']})
        except: continue
    return briefs

# ================= 引擎 2：深度解析逻辑 (供上传使用) =================
def ai_deep_analyze(content, mode="brief"):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    # 根据模式调整 Prompt：爬虫用简版，上传用深度版
    if mode == "deep":
        prompt = f"你作为 Read & Rise 首席教练，深度解析这篇文章：{content}。要求：中英双语提问、匹配思维模型、推荐书籍、高管话术。"
    else:
        prompt = f"简要总结这篇文章的核心要点（中英双语）：{content}"
        
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "你是一位拥有麦肯锡背景的商业教练。"},
                     {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"} # 确保返回 JSON
    }
    # 此处省略 requests.post 逻辑，确保返回解析后的 JSON 数据
    return response.json()['choices'][0]['message']['content']

# 最终保存逻辑会把 briefs 和 deep_articles 合并存入 data.json
