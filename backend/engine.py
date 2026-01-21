# backend/engine.py
import requests
from .crawler import get_search_query

def run_rize_insight(topic, api_key, workflow_id):
    # 调用爬虫逻辑生成精准搜索词
    refined_query = get_search_query(topic)
    
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"workflow_id": workflow_id, "parameters": {"input": refined_query}}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                "title": data.get('cn_title'),
                "one_sentence": data.get('one_sentence'),
                "content": data.get('cn_analysis'),
                "model": data.get('mental_model'),
                "reflection": data.get('reflection')
            }
        return None
    except: return None
