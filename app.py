import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. 页面基本配置
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide", page_icon="🧘")

# 2. 注入专业级 CSS 样式
st.markdown("""
    <style>
    .welcome-text { font-size: 3rem; font-weight: 800; color: #10416F; margin-bottom: 0; }
    .coach-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #10416F;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .model-badge {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .quote-box {
        background-color: #f8f9fa;
        border-left: 5px solid #10416F;
        padding: 20px;
        font-style: italic;
        margin: 20px 0;
        border-radius: 5px;
        color: #333;
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
    st.caption("Intelligence status: Strategic Sync Active")

st.divider()

# --- 数据读取逻辑 ---
articles = []
if os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    except Exception as e:
        st.error(f"数据读取失败，请检查 crawler.py 是否运行成功: {e}")

# --- 核心看板区 (金句 & 能力图) ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 🖋️ 当日金句")
    # 尝试从第一篇文章提炼金句，如果没有则显示默认
    default_quote = "战略的本质是选择不做什么。在这个充满噪音的时代，领导者的首要任务是保持清醒的舍弃感。"
    st.markdown(f'<div class="quote-box">“{default_quote}”</div>', unsafe_allow_html=True)

    st.markdown("### 🧠 今日重点思维模型")
    st.info("**第二曲线 (The Second Curve)**: 当第一条曲线达到巅峰前，就开始投入资源寻找新的增长点。这意味着领导者必须具备在辉煌时感知危机的洞察力。")

with col_right:
    st.markdown("### 📊 今日情报赋能")
    if articles and 'scores' in articles[0]:
        # 汇总今日所有文章的平均分
        try:
            avg_scores = {
                '战略思维': sum(a['scores']['战略思维'] for a in articles) / len(articles),
                '组织进化': sum(a['scores']['组织进化'] for a in articles) / len(articles),
                '决策韧性': sum(a['scores']['决策韧性'] for a in articles) / len(articles),
                '行业洞察': sum(a['scores']['行业洞察'] for a in articles) / len(articles),
                '技术视野': sum(a['scores']['技术视野'] for a in articles) / len(articles),
            }
            chart_data = pd.DataFrame(list(avg_scores.items()), columns=['维度', '提升分值'])
            st.bar_chart(chart_data.set_index('维度'))
        except:
            st.warning("评分数据解析中，请稍后刷新...")
    else:
        st.caption("暂无动态评分数据，请运行最新版爬虫。")

st.divider()

# --- 资讯详情区 ---
st.markdown("### 🏹 深度解析：全球商业内参")

if not articles:
    st.warning("目前没有最新资讯。请确保 crawler.py 已成功运行并同步到服务器。")
else:
    for art in articles:
        with st.container():
            st.markdown(f'''
                <div class="coach-card">
                    <p style="color:#0d47a1; font-weight:700; margin-bottom:5px;">{art.get('source', 'GLOBAL INSIGHT')}</p>
                    <h2 style="margin-top:0;">{art.get('title')}</h2>
                </div>
            ''', unsafe_allow_html=True)
            
            # 兼容新旧数据结构
            content = art.get('analysis') if art.get('analysis') else art.get('content', '内容解析中...')
            
            st.markdown(content)
            st.link_button(f"🌐 阅读原文: {art.get('title')}", art.get('link'))
            st.markdown("<br>", unsafe_allow_html=True)
