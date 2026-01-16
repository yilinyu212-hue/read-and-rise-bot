import os, feedparser, json, requests
from datetime import datetime

# 1. DeepSeek 配置
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 2. 抓取源
RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

def get_ai_analysis(title):
    if not API_KEY:
        return "未检测到 API Key"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位Read & Rise教育策展人。请用中文总结文章核心观点（100字），标注难度(A1-C2)，并提取3个核心词汇（含释义例句）。"},
            {"role": "user", "content": f"文章标题: {title}"}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 解析暂时不可用，请点击链接阅读原文。错误: {str(e)}"

def run():
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        entry = feed.entries[0]
        
        print(f"正在处理: {entry.title}")
        analysis = get_ai_analysis(entry.title)
        
        articles.append({
            "title": entry.title,
            "source": source,
            "link": entry.link,
            "content": analysis,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print("✅ 任务完成！")

if __name__ == "__main__":
    run()
