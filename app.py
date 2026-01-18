import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. 页面基本配置
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide", page_icon="🏹")

# 2. 注入专业视觉样式
st.markdown("""
    <style>
    .welcome-text { font-size: 3rem; font-weight: 800; color: #10416F; margin-bottom: 0; }
    .leader-card {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 8px solid #10416F; margin-bottom: 20px;
    }
    .en-term { color: #10416F; font-weight: bold; background: #eef2f6; padding: 2px 6px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# 3. 数据加载逻辑 (增加兼容性处理)
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except: return []
    return []

articles = load_data()

# 4. 侧边栏导航
with st.sidebar:
    st.markdown("<h1 style='color: #10416F;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    st.caption("AI Business Coach & English Mentor")
    st.divider()
    menu = st.radio("导航 (Navigation)", ["🚀 今日内参 Briefing", "🧠 思维模型 Library", "🎙️ 英文教练 Coaching"])
    st.divider()
    st.info("💡 **Coach Note**: 卓越的领导者不仅阅读资讯，更在构建认知框架。")

# --- 频道 1: 今日内参 ---
if menu == "🚀 今日内参 Briefing":
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.write(f"📅 Sync Date: {datetime.now().strftime('%Y-%m-%d')} | Global Insight")
    
    if not articles:
        st.info("🔄 **正在同步全球最新内参...**\n\n数据正在从 HBR 和 McKinsey 实时同步并由 AI 拆解中。您可以先去 **‘思维模型’** 频道查看已为您准备好的底层逻辑。")
    else:
        for art in articles:
            with st.container():
                st.markdown(f'<div class="leader-card"><h3>{art.get("title")}</h3><p style="color:gray;">{art.get("source")}</p></div>', unsafe_allow_html=True)
                t1, t2 = st.tabs(["🇨🇳 中文深度拆解", "🇬🇧 English Summary"])
                with t1:
                    st.markdown(art.get('cn_analysis') or art.get('content', '解析中...'))
                    st.link_button("🌐 阅读原文", art.get('link'))
                with t2:
                    st.write(art.get('en_summary', 'Summarizing in progress...'))

# --- 频道 2: 思维模型 (内置常驻内容) ---
elif menu == "🧠 思维模型 Library":
    st.header("🧠 商业思维模型库 (Mental Models)")
    st.write("这些模型是您决策的“底层操作系统”。")
    
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        with st.expander("📈 第二曲线 (The Second Curve)", expanded=True):
            st.markdown("在第一曲线到达巅峰前，启动新增长点。")
            st.graphviz_chart('''
                digraph { node[fontname="SimHei",shape=box,color="#10416F"] 
                "创新点" -> "第二曲线(投入期)" -> "指数增长"; "现有业务" -> "巅峰期" -> "衰退期"; }
            ''')
            

    with m_col2:
        with st.expander("🔬 第一性原理 (First Principles)", expanded=True):
            st.markdown("剥离假设，回归物理本质重新构建。")
            st.graphviz_chart('''
                digraph { node[fontname="SimHei",shape=ellipse,color="#2E7D32"] 
                "问题" -> "拆解假设" -> "原子事实" -> "重新架构"; }
            ''')
            

# --- 频道 3: 英文教练 (内置常驻内容) ---
elif menu == "🎙️ 英文教练 Coaching":
    st.header("🎙️ 领导者表达教练 (Executive Phrasing)")
    
    st.subheader("🔥 核心术语库")
    cols = st.columns(3)
    vocab_list = [
        ("Strategic Pivot", "战略转型"), ("Value Proposition", "价值主张"),
        ("Leverage", "杠杆作用"), ("Scalability", "可扩展性"),
        ("Bottleneck", "瓶颈"), ("Synergy", "协同效应")
    ]
    for i, (word, mean) in enumerate(vocab_list):
        cols[i % 3].markdown(f"<span class='en-term'>{word}</span><br>{mean}", unsafe_allow_html=True)
    
    st.divider()
    st.subheader("💬 会议实战话术")
    st.code("How to say '转型': \n'Given the market volatility, we need to execute a strategic pivot to stay competitive.'", language="text")
    st.code("How to say '杠杆': \n'We should leverage our existing network to accelerate user acquisition.'", language="text")
