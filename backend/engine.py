import requests
import json
from .crawler import fetch

def run_rize_insight(topic, api_key, workflow_id):
    """解析单条内容"""
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"workflow_id": workflow_id, "parameters": {"input": topic}}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json().get('data', {})
            if isinstance(data, str):
                try: data = json.loads(data)
                except: pass
            return {
                "title": data.get('cn_title') or f"专题: {topic[:15]}",
                "one_sentence": data.get('one_sentence') or "正在生成爆点...",
                "content": data.get('cn_analysis') or "内容生成中...",
                "model": data.get('mental_model') or "商业模型分析",
                "reflection": data.get('reflection') or "思考是管理者的核心工作。"
            }
    except: return None

# --- 报错的关键：必须包含这个函数 ---
def sync_global_publications(api_key, workflow_id):
    """一键同步逻辑"""
    articles = fetch()
    results = []
    for art in articles:
        context = f"来源:{art['source']} | 标题:{art['title']} | 摘要:{art['content']}"
        res = run_rize_insight(context, api_key, workflow_id)
        if res:
            res['url'] = art['url']
            results.append(res)
    return results
