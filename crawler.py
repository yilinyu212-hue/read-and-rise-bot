import os, feedparser, requests, json, uuid
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def get_ai_data(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    data = {
        "model": "deepseek-chat", 
        "messages": [
            {"role": "system", "content": "You are a professional Executive Coach and Business English Expert. You specialize in structural thinking and pedagogical content design."},
            {"role": "user", "content": prompt}
        ], 
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Error: {e}")
        return None

def run():
    # --- 1. 外刊：增加深度词汇与句法 ---
    SOURCES = [{"name": "HBR", "url": "https://hbr.org/rss/topic/leadership"}]
    articles = []
    for src in SOURCES:
        feed = feedparser.parse(requests.get(src['url'], headers={"User-Agent": UA}).content)
        if feed.entries:
            e = feed.entries[0]
            prompt = f"""解析《{e.title}》: {{
                'en_excerpt': '100字核心段落',
                'cn_translation': '精准翻译',
                'vocabulary_pro': '单词:翻译, 单词2:翻译 (5个)',
                'syntax_analysis': '拆解文中的一个长难句',
                'logic_flow': ['步骤1','步骤2','步骤3'],
                'output_playbook': {{'speaking': '地道口语金句', 'writing': '专业写作句式'}}
            }}"""
            ai = get_ai_data(prompt)
            if ai:
                ai.update({"id": str(uuid.uuid4())[:8], "source": src['name'], "title": e.title, "date": datetime.now().strftime("%Y-%m-%d")})
                articles.append(ai)
    
    # --- 2. 思维模型：升级为实战手册 ---
    # 定义你要覆盖的模型池
    MODEL_POOL = ["MECE Principle", "SCQA Framework", "First Principles Thinking", "Pareto Principle"]
    models = []
    for m_name in MODEL_POOL:
        m_prompt = f"""深度解析思维模型《{m_name}》: {{
            'name': '模型中英文全称',
            'definition': '中英文双语定义',
            'scenario': '企业管理中的实际应用场景',
            'logic_flow': ['核心组件1', '核心组件2', '核心组件3'],
            'english_template': ['场景话术1', '场景话术2'],
            'coach_tips': '教练给出的使用避坑指南'
        }}"""
        ai_m = get_ai_data(m_prompt)
        if ai_m:
            models.append(ai_m)

    # --- 3. 统一保存数据 ---
    os.makedirs('data', exist_ok=True)
    with open('data/library.json', 'w', encoding='utf-8') as f: json.dump(articles, f, ensure_ascii=False, indent=4)
    with open('data/models.json', 'w', encoding='utf-8') as f: json.dump(models, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": run()
