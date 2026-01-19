import requests, feedparser, json, os, time
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
]

def ai_analyze(title, link):
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"""深度解析文章: "{title}"。返回JSON格式，en_summary和cn_summary必须是字符串列表。"""
    
    try:
        res = requests.post(url, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }, timeout=60)
        content = json.loads(res.json()['choices'][0]['message']['content'])
        content.update({"title": title, "link": link})
        return content
    except: return None

def run_sync():
    # 强制包含每周提问，防止主页显示 KeyError
    data = {
        "briefs": [], 
        "deep_articles": [], 
        "weekly_question": {
            "cn": "面对 2026 的挑战，如何通过‘第一性原理’重构核心竞争力？", 
            "en": "How to leverage First Principles to rebuild competitiveness?"
        },
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # 抓取逻辑同前...
    # (此处省略循环 RSS_SOURCES 的部分，保持原有逻辑即可)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_sync()
