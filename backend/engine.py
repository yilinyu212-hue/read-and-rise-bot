# backend/engine.py
import requests
import json

def run_rize_insight(topic, api_key, workflow_id):
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
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            raw_data = response.json().get('data')
            # 兼容性处理：无论扣子返回的是 JSON 字符串还是对象，统统拿下
            if isinstance(raw_data, str):
                parsed = json.loads(raw_data)
            else:
                parsed = raw_data
            
            # 自动提取你工作流里的那个 'output' 变量
            content = parsed.get('output') or parsed.get('cn_analysis') or "内容生成失败"
            return {
                "title": f"关于 {topic} 的深度洞察",
                "content": content,
                "model": parsed.get('mental_model', '战略决策模型')
            }
        return None
    except Exception as e:
        print(f"Engine Error: {e}")
        return None
