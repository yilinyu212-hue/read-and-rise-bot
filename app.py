import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# 1. 网页配置
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide")

# 2. 增强视觉美感 (CSS)
st.markdown("""
    <style>
    .welcome-text { font-size: 3rem; font-weight: 800; color: #10416F; margin-bottom: 0; }
    .quote-box {
        background-color: #f8f9fa;
        border-left: 5px solid #10416F;
        padding: 20px;
        font-style: italic;
        margin: 20px 0;
        border-radius: 5px;
    }
    .model-card {
        background-color: #10416F;
        color: white;
        padding: 20px;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 头部区域 ---
col_head, col_date = st.columns([3, 1])
with col_head:
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.markdown("#### 欢迎回到您的 AI Business Coach 空间")
with col_date:
    st.markdown(f"### 📅 {datetime.now().strftime('%Y-%m-%d')}")
    st.caption("Intelligence status: Operational")

st.divider()

# --- 核心看板区 ---
col_left, col_right = st.columns([2, 1])

with col_left:
    # 1. 今日金句 (这里可以之后从 data.json 动态抓取，现在先放一个标志性的)
    st.markdown("### 🖋️ 当日金句")
    st.markdown("""
    <div class="quote-box">
        “战略的本质是选择不做什么。在这个充满噪音的时代，领导者的首要任务是保持清醒的舍弃感。”
    </div>
    """, unsafe_allow_html=True)

    # 2. 今日思维模型
    st.markdown('<div class="model-card">', unsafe_allow_html=True)
    st.markdown("### 🧠 今日思维模型：**第二曲线 (The Second Curve)**")
    st.write("当第一条曲线达到巅峰前，就开始投入资源寻找新的增长点。这意味着领导者必须具备在辉煌时感知危机的洞察力。")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # 3. 能力雷达图 (Radar Chart)
    st.markdown("### 📊 今日情报赋能")
    # 模拟今日文章涵盖的领导力维度
    df = pd.DataFrame(dict(
        r=[8, 7, 9, 6, 8],
        theta=['战略思维','组织进化','技术视野','决策韧性','行业洞察']))
    
    # 简单通过 Streamlit 条形图展示，或者使用更高级的 plotly
    st.bar_chart(df.set_index('theta'))
    st.caption("基于今日全球资讯，您的“战略思维”与“技术视野”获得显著增强。")

st.divider()

# --- 资讯详情区 ---
st.markdown("### 🏹 深度解析：全球商业内参")
if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
    for art in articles:
        with st.expander(f"📖 {art.get('title')}", expanded=True):
            st.markdown(art.get('content'))
            st.link_button("🌐 阅读原文", art.get('link'))
