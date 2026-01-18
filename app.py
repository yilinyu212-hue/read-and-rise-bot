import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. 页面配置
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide")

# 2. 侧边栏导航 (打造平台感)
with st.sidebar:
    st.markdown("### 🏹 Read & Rise")
    st.caption("Empowering Leaders with Global Insights")
    menu = st.radio("导航 (Navigation)", ["🚀 今日内参 Briefing", "🧠 思维模型 Library", "📖 英文教练 Coaching"])
    st.divider()
    st.markdown("#### 💬 Coach Status")
    st.success("AI Coach is Online")

# --- 核心数据加载 ---
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

articles = load_data()

# --- 频道 1：今日内参 ---
if menu == "🚀 今日内参 Briefing":
    st.markdown('<p style="font-size:3rem; font-weight:800; color:#10416F; margin-bottom:0;">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.write(f"📅 {datetime.now().strftime('%Y-%m-%d')} | 您的全球商业同步已完成")
    
    # 搜索框 (增加交互感)
    search = st.text_input("🔍 搜索关键词 (Search keywords):", placeholder="e.g. AI, Management, Strategy")

    col_main, col_stats = st.columns([2, 1])
    
    with col_main:
        if not articles:
            st.warning("内容正在生成中，请稍后...")
        else:
            for art in articles:
                if search.lower() in art['title'].lower():
                    with st.expander(f"📌 {art['title']}", expanded=True):
                        tab1, tab2 = st.tabs(["🇨🇳 中文深度拆解", "🇬🇧 English Summary"])
                        with tab1:
                            st.markdown(art.get('cn_analysis', '解析同步中...'))
                        with tab2:
                            st.info(art.get('en_summary', 'Summary syncing...'))
                        st.link_button("🌐 阅读原文 Original Link", art['link'])

    with col_stats:
        st.markdown("### 📊 能力赋能图谱")
        # 这里放置之前的 bar_chart 逻辑
        if articles:
            chart_data = pd.DataFrame(list(articles[0]['scores'].items()), columns=['维度', '分值'])
            st.bar_chart(chart_data.set_index('维度'))

# --- 频道 2：思维模型馆 ---
elif menu == "🧠 思维模型 Library":
    st.header("🧠 商业思维模型库")
    st.write("掌握全球顶尖决策者的“底层逻辑”。")
    # 示例数据
    models = {
        "第一性原理 (First Principles)": "Going back to the basic truths and building up from there.",
        "第二曲线 (The Second Curve)": "Finding new growth before the first peak declines.",
        "MECE原则": "Mutually Exclusive, Collectively Exhaustive."
    }
    for m, d in models.items():
        st.subheader(m)
        st.info(d)

# --- 频道 3：英文教练 ---
elif menu == "📖 英文教练 Coaching":
    st.header("📖 领导者英文教练")
    st.write("帮助您在国际会议和跨国交流中更专业地表达。")
    if articles:
        st.markdown("#### 🔑 今日核心术语 (Key Vocabulary)")
        # 提取 crawler.py 传过来的 vocabulary 字段
        vocab = articles[0].get('vocabulary', {"Strategic Pivot": "战略转型", "Leverage": "杠杆作用/利用"})
        for word, mean in vocab.items():
            st.markdown(f"- **{word}**: {mean}")
