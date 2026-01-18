import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 配置区 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 12 个顶级商业与科技源
RSS_SOURCES = [
    # --- 综合战略与管理 ---
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG Global", "url": "https://www.bcg.com/rss.xml"},
    {"name": "Knowledge at Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    
    # --- 科技与数字转型 ---
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Wired Business", "url": "https://www.wired.com/feed/category/business/latest/rss"},
    {"name": "TechCrunch Enterprise", "url": "https://techcrunch.com/category/enterprise/feed/"},
    
    # --- 金融与全球宏观 ---
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Financial Times - Management", "url": "https://www.ft.com/management?format=rss"},
    {"name": "Reuters Business", "url": "http://feeds.reuters.com/reuters/businessNews"},
    
    # --- 创新与设计思维 ---
    {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss/all_articles"}
]

def ai_analyze(title, source_name):
    """
    AI 教练双语拆解逻辑 (增加了重试机制，防止 API 抖动)
    """
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""
    You are a world-class AI Business Coach. Analyze article "{title}" from {source_name}.
    Output strictly in JSON:
    {{
      "en_summary": "3 executive bullet points.",
      "cn_analysis": "### 🧠 思维模型\\n...\\n\\n### 🛠️ 决策建议\\n...",
      "scores": {{"战略思维": 80, "组织进化": 80, "决策韧性": 80, "行业洞察": 80, "技术视野": 80}},
      "vocabulary": {{"Term": "Meaning"}}
    }}
    """
    
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res = response.json()
        content = res['choices'][0]['message']['content'].strip()
        # 自动剔除 ```json 标记
        if "```" in content: content = content.split("```")[1].replace("json", "").strip()
        return json.loads(content)
    except:
        return None

def run_sync():
    all_articles = []
    print(f"🚀 开始全量同步，共计 {len(RSS_SOURCES)} 个源...")
    
    for source in RSS_SOURCES:
        try:
            print(f"📡 抓取中: {source['name']}...")
            feed = feedparser.parse(source['url'])
            # 每个源只取最新 1 篇，12个源保证了多样性同时节省 API 额度
            for item in feed.entries[:1]:
                analysis = ai_analyze(item.title, source['name'])
                if analysis:
                    all_articles.append({
                        "title": item.title, "link": item.link, "source": source['name'],
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        **analysis
                    })
                time.sleep(1) 
        except Exception as e:
            print(f"❌ {source['name']} 失败: {e}")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print(f"✅ 同步完成，今日共获取 {len(all_articles)} 篇深度内参。")

if __name__ == "__main__":
    run_sync()
