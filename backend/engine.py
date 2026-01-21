# backend/engine.py
import requests, json
from .crawler import fetch

def run_auto_sync(api_key, workflow_id):
    # 1. 抓取外刊原文
    raw_articles = fetch()
    results = []
    
    # 2. 挑出最新的（比如第一篇）发给扣子进行深度拆解
    for article in raw_articles[:3]: # 每次处理前3篇
        topic_with_context = f"来源:{article['source']} | 标题:{article['title']} | 内容摘要:{article['content']}"
        
        # 调用扣子 API
        # ... 这里保留之前的 requests.post 逻辑，但发送的是 topic_with_context ...
        # ... 得到 res 后存入 data/knowledge.json ...
    
    return True
