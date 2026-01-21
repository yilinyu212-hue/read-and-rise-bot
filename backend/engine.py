# backend/engine.py
import requests
import json
from .crawler import fetch

def run_rize_insight(topic, api_key, workflow_id):
    """通用解析引擎：处理单条主题或外刊摘要"""
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "workflow_id": workflow_id,
        "parameters": {"input": topic}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            res_json = response.json()
            data = res_json.get('data', {})
            
            # 如果扣子吐出的是字符串，尝试二次解析
            if isinstance(data, str):
                try: data = json.loads(data)
                except: pass
            
            # 这里的 Key 必须和你在扣子“结束节点”里配置的一模一样
            return {
                "title": data.get('cn_title') or f"专题: {topic[:20]}",
                "one_sentence": data.get('one_sentence') or "正在提炼认知爆点...",
                "content": data.get('cn_analysis') or "深度解析生成中...",
                "model": data.get('mental_model') or "待定模型",
                "reflection": data.get('reflection') or "请思考该趋势对您的影响。"
            }
        return None
    except Exception as e:
        print(f"Engine Error: {e}")
        return None

def sync_global_publications(api_key, workflow_id):
    """一键同步逻辑：串联抓取与 AI 解析"""
    raw_articles = fetch() # 调用 crawler.py 的 fetch
    results = []
    
    for article in raw_articles:
        # 将外刊原文作为输入传给扣子
        prompt_input = f"来源:{article['source']} | 标题:{article['title']} | 内容:{article['content']}"
        parsed_res = run_rize_insight(prompt_input, api_key, workflow_id)
        if parsed_res:
            parsed_res['url'] = article['url'] # 保留原文链接
            results.append(parsed_res)
            
    return results
