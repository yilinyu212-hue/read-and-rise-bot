import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 配置与环境变量 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 12 个全球顶尖商业与科技智库源
RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG Global", "url": "https://www.bcg.com/rss.xml"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Financial Times", "url": "https://www.ft.com/management?format=rss"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss/all_articles"},
    {"name": "Knowledge at Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
    {"name": "Wired Business", "url": "https://www.wired.com/feed/category/business/latest/rss"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/category/enterprise/feed/"}
]

# 您希望 AI 生成精读笔记的书籍清单
BOOKS_TO_READ = [
    "《The Second Curve》- Charles Handy",
    "《Principles》- Ray Dalio",
    "《High Output Management》- Andrew Grove",
    "《Zero to One》- Peter Thiel",
    "《Built to Last》- Jim Collins"
]

# ================= 2. AI 解析引擎 =================
def ai_call(prompt):
    """通用的 AI 调用逻辑，包含严格的 JSON 清洗"""
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res_json = response.json()
        content = res_json['choices'][0]['message']['content'].strip()
        
        # 强力清洗：剔除 Markdown 的 json 标签
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        
        return json.loads(content)
    except Exception as e:
        print(f"❌ AI 解析异常: {e}")
        return None

def analyze_article(title, source_name):
    """外刊深度拆解 Prompt"""
    prompt = f"""
    You are a world-class AI Business Coach. Analyze article "{title}" from {source_name}.
    Output STRICTLY in JSON:
    {{
      "en_summary": "3 executive bullet points in English.",
      "cn_analysis": "### 🧠 思维模型\\n[名称及逻辑]\\n\\n### 🛠️ 决策建议\\n[行动指引]",
      "scores": {{"战略思维": 80, "组织进化": 80, "决策韧性": 80, "行业洞察": 80, "技术视野": 80}},
      "vocabulary": {{"Term": "Chinese Meaning"}}
    }}
    """
    return ai_call(prompt)

def analyze_book(book_name):
    """书籍精读笔记 Prompt"""
    prompt = f"""
    You are an Executive Educator. Provide a deep summary for the book "{book_name}".
    Output STRICTLY in JSON:
    {{
      "book_title": "{book_name}",
      "first_principle": "The one core underlying logic of this book.",
      "insights": ["Key Insight 1", "Key Insight 2", "Key Insight 3"],
      "executive_phrasing": "One powerful English sentence for a high-level meeting."
    }}
    """
    return ai_call(prompt)

# ================= 3. 主运行流程 =================
def run_sync():
    # 初始化数据结构，区分文章和书籍
    final_data = {
        "articles": [],
        "books": [],
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # --- 任务 A: 同步 12 个外刊源 ---
    print(f"📡 启动全球智库同步 (共 {len(RSS_SOURCES)} 个源)...")
    for source in RSS_SOURCES:
        try:
            print(f"正在抓取: {source['name']}...")
            feed = feedparser.parse(source['url'])
            # 每个源取最新 1 篇，确保多样性
            for item in feed.entries[:1]:
                analysis = analyze_article(item.title, source['name'])
                if analysis:
                    analysis.update({
                        "title": item.title,
                        "link": item.link,
                        "source": source['name']
                    })
                    final_data["articles"].append(analysis)
            time.sleep(1.2) # 礼貌间断
        except Exception as e:
            print(f"❌ {source['name']} 抓取失败: {e}")

    # --- 任务 B: 生成书籍精读笔记 ---
    print(f"📚 启动 AI 精读笔记生成 (共 {len(BOOKS_TO_READ)} 本书)...")
    for book in BOOKS_TO_READ:
        print(f"正在领读: {book}...")
        book_res = analyze_book(book)
        if book_res:
            final_data["books"].append(book_res)
        time.sleep(1.5)

    # --- 任务 C: 持久化存储 ---
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 同步完成！今日内参: {len(final_data['articles'])} 篇, 书籍笔记: {len(final_data['books'])} 本。")

if __name__ == "__main__":
    run_sync()
