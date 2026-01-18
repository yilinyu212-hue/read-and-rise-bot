import requests
import feedparser
import json
import os
import time

# 从环境变量获取密钥（GitHub Actions 会自动注入）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("APP_TOKEN")
TABLE_ID = os.getenv("TABLE_ID")

# 订阅源列表：聚焦全球顶尖商业洞察
RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist - Business", "url": "https://www.economist.com/business/rss.xml"}
]

def ai_analyze(title, source_name):
    """
    调用 DeepSeek 扮演 AI Business Coach 进行深度拆解
    """
    print(f"🤖 AI Coach 正在深度拆解: 《{title}》...")
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    你是一位顶尖的 AI Business Coach。请针对文章《{title}》(来源:{source_name}) 进行全方位的商业拆解。
    请务必站在各行各业 Leaders 的高度，按照以下 JSON 格式输出，不要包含任何额外的Markdown格式标记（如 ```json ）：

    {{
      "analysis": "### 🧠 思维模型\\n这里填写思维模型应用...\\n\\n### 📚 关联书籍\\n推荐书籍及核心观点...\\n\\n### 🛠️ 决策参考\\n战略判断与避坑指南...",
      "scores": {{
        "战略思维": 85,
        "组织进化": 75,
        "决策韧性": 70,
        "行业洞察": 90,
        "技术视野": 80
      }}
    }}
    
    注意：analysis 字段中使用 \\n 进行换行。评分必须在 0-100 之间。
    """
    
    try:
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res_json = response.json()
        content_raw = res_json['choices'][0]['message']['content'].strip()
        
        # 尝试解析 JSON 字符串
        return json.loads(content_raw)
    except Exception as e:
        print(f"❌ AI 解析出错: {e}")
        # 返回默认结构，防止程序崩溃
        return {
            "analysis": "### ⚠️ 解析暂时不可用\n教练正在深度思考中，请稍后再试。",
            "scores": {"战略思维": 50, "组织进化": 50, "决策韧性": 50, "行业洞察": 50, "技术视野": 50}
        }

def run_sync():
    all_articles = []
    
    for source in RSS_SOURCES:
        print(f"📡 正在同步源: {source['name']}...")
        feed = feedparser.parse(source['url'])
        
        # 每次只取每个源的前 2 篇最新文章，避免 AI 额度消耗过快
        for item in feed.entries[:2]:
            analysis_data = ai_analyze(item.title, source['name'])
            
            article = {
                "title": item.title,
                "link": item.link,
                "source": source['name'],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "analysis": analysis_data.get("analysis"),
                "scores": analysis_data.get("scores")
            }
            all_articles.append(article)
            time.sleep(1) # 稍作停顿，避免请求过快

    # 保存到本地 data.json，供网页读取
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print(f"✅ 任务完成，已成功解析 {len(all_articles)} 篇深度内参。")

if __name__ == "__main__":
    from datetime import datetime
    run_sync()
