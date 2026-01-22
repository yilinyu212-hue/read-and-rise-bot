import streamlit as st
from backend.crawler import run_crawler
from backend.engine import analyze_article
import json

st.set_page_config(page_title="Read & Rise", layout="wide")

# ====== 侧边栏 ======
st.sidebar.title("📘 Read & Rise")
page = st.sidebar.radio(
    "导航",
    ["🏠 主页", "📰 今日精选", "⚙️ 手动抓取"]
)

# ====== 主页 ======
if page == "🏠 主页":
    st.title("Read & Rise")
    st.subheader("Read Daily · Rise Strategically")

    st.markdown("""
    **为创业者 / 管理者 / 知识型创作者设计的外刊洞察系统**
    
    - 每日精选高质量外刊
    - AI 提炼思维模型
    - 形成可复用的管理认知
    """)

# ====== 今日精选 ======
elif page == "📰 今日精选":
    st.title("今日精选")

    try:
        with open("data/knowledge.json", "r", encoding="utf-8") as f:
            items = json.load(f)

        for item in items[:5]:
            st.markdown(f"### {item['cn_title']}")
            st.write(item.get("cn_analysis", ""))
            st.divider()
    except:
        st.info("暂无内容，请先抓取")

# ====== 手动抓取 ======
elif page == "⚙️ 手动抓取":
    st.title("手动抓取外刊")

    if st.button("🚀 开始抓取"):
        with st.spinner("正在抓取并分析..."):
            run_crawler()
        st.success("抓取完成！")
