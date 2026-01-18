import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. 页面配置
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide")

# 2. 强力 CSS 注入：解决 Preload CSS 报错
st.markdown("""
    <style>
    .welcome-text { font-size: 2.5rem; font-weight: 800; color: #10416F; }
    .english-coach-box {
        background-color: #f0f7ff;
        border-left: 5px solid #007bff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
    .term-highlight { color: #d63384; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 侧边栏导航：增加期待感 ---
with st.sidebar:
    st.title("🏹 Navigation")
    mode = st.radio("切换频道", ["🏠 每日看板", "📖 英文教练特训", "🧠 思维模型库"])
    st.divider()
    st.info("作为您的 English Coach，我建议您每天挑选 3 个专业术语进行会议实战。")

# --- 读取数据 ---
articles = []
if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

# --- 逻辑分流 ---
if mode == "🏠 每日看板":
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🖋️ 当日金句")
        st.info("“Strategic focus is about saying NO to good ideas to make room for GREAT ones.”")
        
        st.subheader("🏹 最新内参解析")
        for art in articles:
            with st.expander(f"📌 {art.get('title')}"):
                st.markdown(art.get('cn_analysis') or art.get('content'))
                st.link_button("🌐 阅读原文", art.get('link'))

    with col2:
        st.subheader("📊 能力赋能")
        # 稳定的图表展示
        chart_data = pd.DataFrame({'维度': ['战略', '组织', '技术', '韧性'], '提升': [90, 85, 70, 80]})
        st.bar_chart(chart_data.set_index('维度'))

elif mode == "📖 英文教练特训":
    st.header("🎙️ Executive English Coaching")
    st.write("从今日资讯中提炼的高管级表达：")
    
    for art in articles:
        vocab = art.get('vocabulary', {"Pivotal": "至关重要的", "Leverage": "利用/杠杆"})
        st.markdown(f"### 来自文章: {art.get('title')}")
        for word, meaning in vocab.items():
            st.markdown(f"""
            <div class="english-coach-box">
                <span class="term-highlight">{word}</span> ({meaning})<br>
                <em>Example: "This strategy is <span class="term-highlight">{word}</span> for our Q3 growth."</em>
            </div>
            """, unsafe_allow_html=True)

elif mode == "🧠 思维模型库":
    st.header("🧠 商业思维模型 Library")
    st.write("沉淀每一天的深度逻辑。")
    # 可以在这里硬编码一些经典的思维导图逻辑
