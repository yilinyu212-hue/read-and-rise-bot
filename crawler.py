import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 环境与配置 =================
# 从 GitHub Secrets 自动获取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 聚焦全球顶尖商业洞察的源
RSS_SOURCES = [
    {"name": "Harvard Business Review", "url": "[https://hbr.org/rss/feed/topics/leadership](https://hbr.org/rss/feed/topics/leadership)"},
    {"name": "McKinsey Insights", "url": "[https://www.mckinsey.com/insights/rss](https://www.mckinsey.com/insights/rss)"},
    {"name": "Economist - Business", "url": "[https://www.economist.com/business/rss.xml](https://www.economist.com/business/rss.xml)"}
]

# ================= 2. AI 教练深度解析模块 =================
def ai_analyze(title, source_name):
    """
    扮演 AI Business Coach & English Mentor 
    进行结构化双语拆解、能力评分及词汇提取
    """
    print(f"🤖 AI Coach 正在深度拆解: 《{title}》...")
    url = "[https://api.deepseek.com/chat/completions](https://api.deepseek.com/chat/completions)"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 针对 Leaders 的专业 Prompt，强制要求 JSON 格式
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
    
    Important: Use \\n for line breaks in the cn_analysis field. 
    Do NOT include any Markdown code block markers like ```json in your response.
    """
    
    try:
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res_json = response.json()
        
        # 获取 AI 返回的原始字符串
        content_raw = res_json['choices'][0]['message']['content'].strip()
        
        # --- 健壮性处理：剔除 AI 可能自带的 Markdown 代码块标记 ---
        if content_raw.startswith("```"):
            # 兼容 ```json 或 ``` 格式
            lines = content_raw.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content_raw = "\n".join(lines).strip()
            
        # 尝试转为 JSON
        return json.loads(content_raw)
        
    except Exception as e:
        print(f"❌ 解析失败 ({title}): {e}")
        # 兜底数据，确保流程不中断
        return {
            "en_summary": "Insight processing in progress...",
            "cn_analysis": "### ⚠️ 解析同步中\n教练正在深度解析此篇外刊，请稍后刷新查看深度洞察。",
            "scores": {"战略思维": 60, "组织进化": 60, "决策韧性": 60, "行业洞察": 60, "技术视野": 60},
            "vocabulary": {"Strategic Shift": "战略转型", "Benchmark": "标杆"}
        }

# ================= 3. 主运行逻辑 =================
def run_sync():
    all_articles = []
    
    for source in RSS_SOURCES:
        print(f"📡 正在拉取: {source['name']}...")
        try:
            feed = feedparser.parse(source['url'])
            # 选取每个源最新的 2 篇，保持高质量与低配额消耗
            for item in feed.entries[:2]:
                analysis_result = ai_analyze(item.title, source['name'])
                
                # 组装完整数据对象
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
                time.sleep(1.5) # 礼貌频率，防止被封 IP
                
        except Exception as e:
            print(f"❌ 源 {source['name']} 抓取异常: {e}")

    # --- 最终持久化存储 ---
    # 这会覆盖旧的 data.json，生成全新的结构化数据供 app.py 读取
    output_path = "data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 任务大功告成！已为 Leaders 同步 {len(all_articles)} 篇双语商业内参。")

if __name__ == "__main__":
    run_sync()
