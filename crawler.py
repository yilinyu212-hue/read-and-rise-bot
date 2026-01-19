import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 配置中心 =================
# 必须在 GitHub Secrets 中配置 DEEPSEEK_API_KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 10个精选全球智库/商业源
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

# ================= 2. AI 深度解析函数 =================
def ai_deep_analyze(title, link):
    if not DEEPSEEK_API_KEY:
        print("❌ 错误: 未检测到 API KEY")
        return None

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 强制 AI 输出标准列表格式，解决 app.py 的 TypeError 报错
    prompt = f"""
    You are the Chief AI Coach for 'Read & Rise'. Deeply analyze the business article: "{title}".
    Return a STRICT JSON object with these fields:
    1. "en_summary": [3 key points in English as a LIST of strings]
    2. "cn_summary": [3条核心中文摘要（列表格式）]
    3. "golden_sentences": [{{ "en": "quote", "cn": "对应中文金句" }}] (Extract 2)
    4. "vocab_bank": [{{ "word": "term", "meaning": "中文含义", "example": "English example" }}] (Extract 3)
    5. "case_study": "Deep analysis: Background-Challenge-Decision-Result"
    6. "reflection_flow": ["Question 1 about Layout", "Question 2 about Planning", "Question 3 Actionable Advice"]
    7. "related_model": "The most relevant mental model"
    8. "scores": {{ "Strategy": 85, "Insight": 90, "Leadership": 80, "Innovation": 75, "Decision": 85 }}
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional executive coach. Always output valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        res_json = response.json()
        analysis = json.loads(res_json['choices'][0]['message']['content'])
        
        # 补全基础字段
        analysis["title"] = title
        analysis["link"] = link
        analysis["sync_date"] = datetime.now().strftime("%Y-%m-%d")
        return analysis
    except Exception as e:
        print(f"❌ 解析文章失败 {title}: {str(e)}")
        return None

# ================= 3. 主运行程序 =================
def run_sync():
    print(f"🕒 [{datetime.now()}] 启动智库同步...")
    
    # 初始化数据结构（包含 weekly_question，防止主页 KeyError）
    new_data = {
        "briefs": [], 
        "deep_articles": [], 
        "weekly_question": {
            "cn": "面对 2026 的挑战，如何通过‘第一性原理’重构核心竞争力？", 
            "en": "How to leverage First Principles to rebuild competitiveness?"
        },
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # 尝试读取旧数据中的深度文章，避免被覆盖
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)
                new_data["deep_articles"] = old_data.get("deep_articles", [])
                # 如果旧数据有自定义问题，可以保留
                new_data["weekly_question"] = old_data.get("weekly_question", new_data["weekly_question"])
        except:
            print("⚠️ 旧 data.json 格式损坏，将创建新文件")

    # 遍历 RSS 源抓取
    for source in RSS_SOURCES:
        print(f"📡 正在抓取: {source['name']}...")
        try:
            feed = feedparser.parse(source['url'])
            if feed.entries:
                # 获取该源最新的一篇文章
                latest = feed.entries[0]
                analysis = ai_deep_analyze(latest.title, latest.link)
                
                if analysis:
                    analysis["source"] = source['name']
                    new_data["briefs"].append(analysis)
                    print(f"✅ 成功解析: {source['name']}")
                
                # 间隔 2 秒，防止 API 频率限制
                time.sleep(2)
        except Exception as e:
            print(f"❌ 源 {source['name']} 抓取失败: {e}")

    # 最终写入文件
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    
    print(f"🏁 同步完成！共抓取 {len(new_data['briefs'])} 篇新资讯。")

if __name__ == "__main__":
    run_sync()
