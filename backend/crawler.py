import feedparser
import requests

def get_full_text(url):
    """
    【Read & Rise 核心插件】
    利用 Jina AI 接口突破外刊摘要限制，抓取网页全文。
    """
    # 在 URL 前加上 r.jina.ai/ 即可直接获取网页的干净文本
    jina_url = f"https://r.jina.ai/{url}"
    try:
        # 设置 15 秒超时，确保抓取稳定性
        response = requests.get(jina_url, timeout=15)
        if response.status_code == 200:
            # 截取前 2500 字，这是 AI 生成高质量深度解析的最佳长度
            return response.text[:2500]
        return ""
    except Exception as e:
        print(f"全文抓取失败: {e}")
        return ""

def fetch():
    """
    抓取外刊 RSS 源并同步全文内容
    """
    # 针对 Educator（教育者）定位，选取了哈佛商业评论和麦肯锡作为核心源
    RSS_SOURCES = [
        {"name": "HBR", "url": "https://hbr.org/rss/feed/topics/leadership"},
        {"name": "McKinsey", "url": "https://www.mckinsey.com/insights/rss"}
    ]
    
    articles = []
    for src in RSS_SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            if feed.entries:
                # 获取最新的一篇文章
                entry = feed.entries[0]
                
                # --- 核心改进：调用全文抓取函数 ---
                full_content = get_full_text(entry.link)
                
                articles.append({
                    "source": src["name"],
                    "title": entry.title,
                    # 如果全文抓取成功则使用全文，否则降级使用摘要
                    "content": full_content if len(full_content) > 100 else entry.get("summary", ""),
                    "url": entry.link
                })
                print(f"成功抓取 {src['name']}: {entry.title}")
        except Exception as e:
            print(f"抓取 {src['name']} 出错: {e}")
            continue
            
    return articles
