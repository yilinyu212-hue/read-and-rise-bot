import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 配置区 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 订阅源：涵盖全球顶尖商业内参
RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey Insights", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "Economist - Business", "url": "https://www.economist.com/business/rss.xml"}
]

# ================= AI 教练解析逻辑 =================
def ai_analyze(title, source_name):
    """
    扮演 AI Business Coach & English Mentor 
    进行双语拆解、打分并提取高阶词汇
    """
    print(f"🤖 AI Coach 正在深度拆解: 《{title}》...")
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 针对 Leaders 的专业 Prompt
    prompt = f"""
    You are a world-class AI Business Coach and Executive English Mentor. 
    Analyze the article "{title}" from {source_name}.
    
    Please provide the output STRICTLY in the following JSON format:
    {{
      "en_summary": "A concise executive summary in professional English (3 bullet points).",
      "cn_analysis": "### 🧠 思维模型\\n[模型名称及应用]\\n\\n### 📚 关联书籍\\n[推荐书籍及核心观点]\\n\\n### 🛠️ 决策建议\\n[给Leader的具体行动指引]",
      "scores": {{
        "战略思维": 85,
        "组织进化": 75,
        "决策韧性": 70,
        "行业洞察": 90,
        "技术视野": 80
      }},
      "vocabulary": {{
        "Term 1": "中文意思",
        "Term 2": "中文意思"
      }}
    }}
    
    Important: Use \\n for line breaks in the cn_analysis field. Do not include any Markdown block markers like ```json.
    """
    
    try:
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res_json = response.json()
        
        # 提取并清理内容
        content_raw = res_json['choices'][0]['message']['content'].strip()
        # 移除可能存在的 Markdown 代码块标记
        if content_raw.startswith("```"):
            content_raw = content_raw.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            
        return json.loads(content_raw)
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        # 兜底数据，防止网页崩溃
        return {
            "en_summary": "English insights are being processed...",
            "cn_analysis": "### ⚠️ 正在同步\n教练正在深度解析此文章，请稍后刷新。",
            "scores": {"战略思维": 60, "组织进化": 60, "决策韧性": 60, "行业洞察": 60, "技术视野": 60},
            "vocabulary": {"Insight": "洞察", "Strategy": "战略"}
        }

# ================= 任务运行主逻辑 =================
def run_sync():
    all_articles = []
    
    for source in RSS_SOURCES:
        print(f"📡 正在抓取: {source['name']}...")
        try:
            feed = feedparser.parse(source['url'])
            # 每个源只取前 2 篇最新文章，确保质量
            for item in feed.entries[:2]:
                analysis_result = ai_analyze(item.title, source['name'])
                
                article_data = {
                    "title": item.title,
                    "link": item.link,
                    "source": source['name'],
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "en_summary": analysis_result.get("en_summary"),
                    "cn_analysis": analysis_result.get("cn_analysis"),
                    "scores": analysis_result.get("scores"),
                    "vocabulary": analysis_result.get("vocabulary")
                }
                all_articles.append(article_data)
                time.sleep(1) # 礼貌抓取
        except Exception as e:
            print(f"❌ 源 {source['name']} 抓取异常: {e}")

    # 保存到服务器本地 data.json
    output_path = "data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 同步完成！共处理 {len(all_articles)} 篇精英内参。")

if __name__ == "__main__":
    run_sync()
