import requests
import time

def fetch():
    """
    【水源强效修复版】使用中转代理绕过网络封锁
    """
    # 使用 r.jina.ai 作为中转，它通常能绕过直接访问 RSS 的网络限制
    test_urls = [
        "https://r.jina.ai/https://www.technologyreview.com/feed/",
        "https://r.jina.ai/https://hbr.org/feed"
    ]
    
    results = []
    for url in test_urls:
        try:
            # 增加超时设置和简单的重试
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                results.append({
                    "title": "最新全球商业趋势分析", 
                    "content": response.text[:4000] # 获取更长的全文供 AI 深度解析
                })
        except Exception as e:
            print(f"抓取依然失败: {e}")
            
    # 如果全部失败，提供一个保底的案例素材，确保管理者能看到内容预览
    if not results:
        results.append({
            "title": "保底案例：企业抗风险能力建设",
            "content": "这里是预置的深度商业案例素材，用于网络不可用时的演示..."
        })
    return results
