import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 配置中心 =================
# 请确保在 GitHub Secrets 或环境变量中设置了 DEEPSEEK_API_KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 10+ 个全球顶级智库源
RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "BCG Global", "url": "https://www.bcg.com/rss.xml"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"},
    {"name": "Knowledge@Wharton", "url": "https://knowledge.wharton.upenn.edu/feed/"},
    {"name": "Strategy+Business", "url": "https://www.strategy-business.com/rss/all_articles"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/latest/rss"},
    {"name": "Wired Business", "url": "https://www.wired.com/feed/category/business/latest/rss"}
]

# ================= 2. AI 深度解析引擎 =================
def ai_deep_analyze(title, link):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 强制要求 AI 产出中英双语及深度内容
    prompt = f"""
    You are the Chief AI Coach for 'Read & Rise'. Deeply analyze the business article: "{title}".
    
    Return a strictly valid JSON object with the following fields:
    1. "en_summary": 3 bullet points summary in English.
    2. "cn_summary": 3条核心中文摘要（深度洞察）.
    3. "golden_sentences": [{{ "en": "quote", "cn": "对应中文金句" }}] (Extract 2 sentences).
    4. "vocab_bank": [{{ "word": "term", "meaning": "中文含义", "example": "English example sentence" }}] (Extract 3 professional terms).
    5. "case_study": "中英双语解析：背景-挑战-决策-结果 (Background-Challenge-Decision-Result)".
    6. "reflection_flow": ["问题1: 关于布局", "问题2: 关于规划", "问题3: 实践建议"].
    7. "related_model": "The most relevant mental model (e.g., First Principles, Anti-fragile)".
    8. "scores": {{ "Strategy": 85, "Insight": 90, "Leadership": 80, "Innovation": 75, "Decision": 85 }}
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional executive coach with a McKinsey background. You provide high-density, actionable insights."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        res_json = response.json()
        analysis = json.loads(res_json['choices'][0]['message']['content'])
        
        # 补充基础信息
        analysis["title"] = title
        analysis["link"] = link
        analysis["sync_date"] = datetime.now().strftime("%Y-%m-%d")
        return analysis
    except Exception as e:
        print(f"❌ Error analyzing {title}: {e}")
        return None

# ================= 3. 主运行逻辑 =================
def run_sync():
    print(f"🚀 [{datetime.now()}] Starting Global Insight Sync...")
    
    # 初始化数据结构
    data = {
        "briefs": [], 
        "deep_articles": [], 
        "weekly_question": {
            "cn": "面对剧变的 2026，你的企业布局是否具备‘反脆弱’特征？", 
            "en": "In a volatile 2026, does your business layout possess 'anti-fragile' characteristics?"
        },
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # 如果存在旧数据，读取它以保留手动上传的 deep_articles
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)
                data["deep_articles"] = old_data.get("deep_articles", [])
                data["weekly_question"] = old_data.get("weekly_question", data["weekly_question"])
        except Exception as e:
            print(f"⚠️ Could not read old data.json: {e}")

    # 遍历抓取 10+ 源
    for source in RSS_SOURCES:
        print(f"📡 Scanning: {source['name']}...")
        try:
            feed = feedparser.parse(source['url'])
            if not feed.entries:
                continue
            
            # 每次只取每个源最新的一篇，保证质量和 API 额度
            latest_entry = feed.entries[0]
            
            # AI 解析
            analysis = ai_deep_analyze(latest_entry.title, latest_entry.link)
            if analysis:
                analysis["source"] = source['name']
                data["briefs"].append(analysis)
                print(f"✅ Success: {latest_entry.title}")
            
            # 稍微停顿，避免请求过快被封或 API 频率限制
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Failed to sync {source['name']}: {e}")

    # 保存结果
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"🏁 [{datetime.now()}] All sync tasks completed.")

if __name__ == "__main__":
    # 确保 API KEY 存在
    if not DEEPSEEK_API_KEY:
        print("❌ ERROR: DEEPSEEK_API_KEY not found in environment variables.")
    else:
        run_sync()
