import streamlit as st
import pandas as pd
import os

# 1. 更加稳健的 CSS：避免使用可能导致加载错误的外部链接
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stChart { background-color: white; padding: 15px; border-radius: 10px; shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .welcome-text { color: #10416F; font-size: 2.5rem; font-weight: 800; margin-bottom: 0; }
    .coach-quote { font-size: 1.1rem; color: #555; border-left: 4px solid #10416F; padding-left: 15px; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 头部 (Hi, Leaders!) ---
st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
st.write(f"📅 今日日期：{pd.Timestamp.now().strftime('%Y-%m-%d')} | 您的 AI 商业教练已就绪")

st.divider()

# --- 主内容布局 ---
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.markdown("### 🏹 今日深度洞察 (Intelligence)")
    # 这里放置你的文章循环逻辑 (如前所述)
    if os.path.exists("data.json"):
        # ... 文章展示代码 ...
        st.info("数据已从飞书知识库同步，AI 已完成思维模型拆解。")

with col_stats:
    st.markdown("### 📊 今日能力赋能")
    
    # 模拟今日情报对 Leader 能力的提升数值
    # 这里的数值未来可以由 crawler.py 根据 AI 评分自动生成
    chart_data = pd.DataFrame({
        '维度': ['战略思维', '组织进化', '决策韧性', '行业洞察', '技术视野'],
        '提升分值': [92, 85, 78, 95, 88]
    })
    
    # 使用 Streamlit 官方最稳定的条形图，不依赖外部 CSS
    st.bar_chart(chart_data.set_index('维度'))
    
    st.markdown("""
    > **教练点评**：
    > 今日资讯侧重于**行业洞察**与**战略思维**。建议重点关注《麦肯锡》关于 AI 组织变革的案例，这将直接优化您的“组织进化”维度。
    """)
