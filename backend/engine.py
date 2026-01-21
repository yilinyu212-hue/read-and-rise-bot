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
            res_json = response.json()
            # 兼容处理：Coze 的 workflow 返回数据在 'data' 字段里
            raw_data = res_json.get('data')
            
            # 如果是字符串形式的 JSON，解析它
            if isinstance(raw_data, str):
                parsed = json.loads(raw_data)
            else:
                parsed = raw_data if raw_data else {}

            # 提取内容：优先找你的具体字段，找不到就拿全量 output
            content = parsed.get('output') or parsed.get('cn_analysis') or str(parsed)
            model = parsed.get('mental_model') or "决策者心智模型"
            title = parsed.get('cn_title') or f"关于 {topic} 的深度拆解"

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
