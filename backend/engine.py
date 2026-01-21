cat << 'EOF' > backend/engine.py
import requests
import json

def run_rize_insight(topic, api_key, workflow_id):
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"workflow_id": workflow_id, "parameters": {"input": topic}}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            res_json = response.json()
            raw_data = res_json.get('data')
            
            # 核心修正：深度解析可能嵌套的 JSON 字符串
            if isinstance(raw_data, str):
                try:
                    parsed = json.loads(raw_data)
                except:
                    # 如果不是标准JSON，就直接作为内容
                    return {"title": f"关于 {topic}", "content": raw_data, "model": "通用模型"}
            else:
                parsed = raw_data if raw_data else {}

            # 提取字段，如果字段还是 JSON 字符串，再解析一次
            content = parsed.get('cn_analysis') or parsed.get('output')
            if isinstance(content, str) and content.startswith('{'):
                try:
                    inner_json = json.loads(content)
                    content = inner_json.get('cn_analysis') or inner_json.get('output') or content
                except: pass

            return {
                "title": parsed.get('cn_title') or f"关于 {topic} 的专题研究",
                "content": content or "暂无详细解析内容",
                "model": parsed.get('mental_model') or "决策心智模型"
            }
        return None
    except Exception as e:
        return None
EOF
