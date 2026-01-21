# backend/engine.py

import requests
import json

def run_rize_insight(topic, api_key, workflow_id):
    """
    负责调用扣子 API 并进行数据清洗
    """
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
            raw_data = res_json.get('data')
            
            # 自动解析字符串格式的 JSON
            if isinstance(raw_data, str):
                parsed = json.loads(raw_data)
            else:
                parsed = raw_data if raw_data else {}

            # 数据提取逻辑
            content = parsed.get('output') or parsed.get('cn_analysis') or "解析失败：请检查扣子工作流输出"
            model = parsed.get('mental_model') or "决策者心智模型"
            title = parsed.get('cn_title') or f"关于 {topic} 的深度分析"

            return {
                "title": title,
                "content": content,
                "model": model
            }
        else:
            print(f"API Error: {response.text}")
            return None
    except Exception as e:
        print(f"Engine Exception: {e}")
        return None
