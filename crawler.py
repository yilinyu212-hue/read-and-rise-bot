import os, feedparser, requests, json
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")

def get_ai_coach_data(title):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    prompt = f"""
    作为顶级英语培训师与管理教练，请针对《{title}》制作深度讲义。
    必须按以下 JSON 格式返回：
    {{
      "level": "Advanced (C1)",  // 根据难度选: Intermediate (B2), Advanced (C1), Expert (C2)
      "tags": ["Leadership", "Innovation"],
      "en_excerpt": "挑选一段包含高级语法（如虚拟语气、倒装、伴随状语）的原文(60-100 words)。",
      "cn_translation": "信达雅的中文翻译。",
      "vocabulary_pro": "Markdown格式：词汇+搭配+职场场景例句。",
      "syntax_analysis": "Markdown格式：拆解文中的长难句，并说明其在商务写作中的妙处。",
      "output_playbook": {{
          "speaking": "如果你在会议中引用此文，请使用此模板：'As highlighted in the latest analysis regarding...', 'This leads to a pivotal question for our team...'",
          "writing": "如果你写一份日报或周报，可以套用的高阶句型：'In light of current trends in...', 'It is imperative that we recalibrate our approach to...'"
      }},
      "action": "实战行动建议。"
    }}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are a senior Business English pedagogical expert."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except: return "{}"

def run():
    SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"},
        {"name": "Economist", "url": "https://www.economist.com/briefing/rss.xml"},
        {"name": "WSJ", "url": "https://feeds.a.dj.com/rss/WSJBusiness.xml"},
        {"name": "Fortune", "url": "https://fortune.com/feed/"},
        {"name": "FT", "url": "https://www.ft.com/?format=rss"},
        {"name": "Forbes", "url": "https://www.forbes.com/innovation/feed/"},
        {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"},
        {"name": "Atlantic", "url": "https://www.theatlantic.com/feed/all/"}
    ]
    results = []
    for src in SOURCES:
        try:
            resp = requests.get(src['url'], headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            feed = feedparser.parse(resp.content)
            if feed.entries:
                entry = feed.entries[0]
                ai_json = json.loads(get_ai_coach_data(entry.title))
                results.append({
                    "source": src['name'], "title": entry.title,
                    "level": ai_json.get('level', 'C1'),
                    "en_text": ai_json.get('en_excerpt', ''),
                    "cn_text": ai_json.get('cn_translation', ''),
                    "tags": ai_json.get('tags', []),
                    "vocabulary": ai_json.get('vocabulary_pro', ''),
                    "syntax": ai_json.get('syntax_analysis', ''),
                    "playbook": ai_json.get('output_playbook', {}),
                    "action": ai_json.get('action', ''),
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
        except: continue
    with open('data/library.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
