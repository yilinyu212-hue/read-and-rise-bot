cat << 'EOF' > backend/engine.py
import requests
import json
from .crawler import fetch

def run_rize_insight(topic, api_key, workflow_id):
    """单条主题处理逻辑（保留原有功能）"""
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"workflow_id": workflow_id, "parameters": {"input": topic}}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json().get('data', {})
            # 兼容处理：如果扣子吐出的是 JSON 字符串，尝试解析
            if isinstance(data, str): 
                try: data = json.loads(data)
                except: pass
            
            return {
                "title": data.get('cn_title') or f"关于 {topic} 的深度分析",
                "content": data.get('cn_analysis') or "解析内容生成中...",
                "model": data.get('mental_model') or "决策心智模型",
                "one_sentence": data.get('one_sentence') or "思考比勤奋更重要。",
                "reflection": data.get('reflection') or "现在的策略是否具备可持续性？"
            }
        return None
    except:
        return None

def sync_global_publications(api_key, workflow_id):
    """一键同步外刊逻辑（新功能）"""
    # 1. 启动爬虫
    raw_articles = fetch()
    processed_results = []
    
    # 2. 选取每个源的最新一条进行加工（避免 API 消耗过大）
    for article in raw_articles:
        context = f"来源:{article['source']} | 标题:{article['title']} | 摘要:{article['content']}"
        res = run_rize_insight(context, api_key, workflow_id)
        if res:
            res['source'] = article['source']
            res['url'] = article['url']
            processed_results.append(res)
            
    return processed_results
EOF
