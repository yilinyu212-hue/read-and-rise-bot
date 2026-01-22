import openai
import json
from .crawler import fetch 

def run_rize_insight(title, source, content):
    client = openai.OpenAI(api_key="sk-4ee83ed8d53a4390846393de5a23165f", base_url="https://api.deepseek.com")
    prompt = f"请解析《{source}》的文章《{title}》，输出JSON格式包含 golden_quote, punchline, read, rise。"
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"golden_quote": "Keep Growing.", "punchline": "正在萃取中", "read": "加载中", "rise": "规划中"}

def sync_global_publications():
    articles = fetch()
    processed = []
    for a in articles:
        res = run_rize_insight(a['title'], a['source'], a['content'])
        processed.append({**a, **res})
    return processed
