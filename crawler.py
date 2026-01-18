import requests
import feedparser
import json
import os
import time
from datetime import datetime

# ================= 1. 环境配置 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

RSS_SOURCES = [
    {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/business/rss.xml"},
    {"name": "Fortune", "url": "https://fortune.com/feed/"}
]

# 核心知识库（用于 AI 联动）
BOOKS_TO_READ = ["《The Second Curve》", "《Principles》", "《High Output Management》", "《Zero to One》"]
MENTAL_MODELS = ["第一性原理", "第二曲线", "飞轮效应", "反脆弱", "复利效应", "机会成本"]

# ================= 2. AI 解析引擎 =================
def ai_call(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    try:
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60)
        content = response.json()['choices'][0]['message']['content'].strip()
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        return json.loads(content)
    except: return None

# ================= 3. 同步主流程 =================
def run_sync():
    final_data = {"articles": [], "books": [], "weekly_question": "", "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    all_titles = []
    
    print("📡 同步智库源并建立知识联动...")
    for source in RSS_SOURCES:
        feed = feedparser.parse(source['url'])
        for item in feed.entries[:1]:
            # 核心：要求 AI 进行跨维度联动
            prompt = f"""Analyze article '{item.title}'. 
            1. Match with ONE model from {MENTAL_MODELS}. 
            2. Suggest ONE book from {BOOKS_TO_READ} for deep study.
            Output JSON: {{
              "en_summary": "3 executive points",
              "cn_analysis": "### 🧠 思维模型\\n...\\n\\n### 🛠️ 决策建议\\n...",
              "related_model": "模型名称",
              "related_book": "关联书籍名",
              "scores": {{"战略": 80, "组织": 85, "决策": 75, "视野": 90, "洞察": 80}},
              "vocabulary": {{"Term": "Meaning"}}
            }}"""
            res = ai_call(prompt)
            if res:
                res.update({"title": item.title, "link": item.link, "source": source['name']})
                final_data["articles"].append(res)
                all_titles.append(item.title)

    print("📚 生成书籍精读笔记...")
    for book in BOOKS_TO_READ:
        res = ai_call(f"Provide summary for '{book}'. JSON: {{'book_title': '{book}', 'first_principle': '...', 'insights': ['...'], 'executive_phrasing': '...'}}")
        if res: final_data["books"].append(res)

    print("🎙️ 生成本周启发式提问...")
    q_res = ai_call(f"Based on titles {all_titles[:5]}, generate ONE deep coaching question for a CEO. JSON: {{'q': '...'}}")
    final_data["weekly_question"] = q_res.get('q', "如何利用第一性原理重构你的核心业务？") if q_res else "如何平衡短期利润与长期增长？"

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("✅ 全量联动同步完成")

if __name__ == "__main__":
    run_sync()
