import os, feedparser, json, requests
from datetime import datetime

# 1. 配置
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions" # 修正了地址

def get_ai_analysis(title):
    if not API_KEY or len(API_KEY) < 10:
        return "错误：GitHub Secrets 里的 DEEPSEEK_API_KEY 没填对，请重新检查！"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位教育专家，请用中文总结文章核心观点。"},
            {"role": "user", "content": f"文章标题: {title}"}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        res_json = response.json()
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            return f"AI报错：{json.dumps(res_json)}"
    except Exception as e:
        return f"网络报错：{str(e)}"

def run():
    # 抓取经济学人
    feed = feedparser.parse("https://www.economist.com/briefing/rss.xml")
    articles = []
    
    for entry in feed.entries[:3]:
        print(f"正在解析: {entry.title}")
        analysis = get_ai_analysis(entry.title)
        articles.append({
            "title": entry.title,
            "source": "The Economist",
            "link": entry.link,
            "content": analysis,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
