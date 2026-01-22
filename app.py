import streamlit as st
from backend import engine

st.set_page_config(page_title="Read & Rise", layout="wide", initial_sidebar_state="collapsed")

# 自定义 CSS 增加视觉舒适度
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMarkdown { line-height: 1.6; font-size: 1.05rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Read & Rise | Executive Insight")
st.caption("全球外刊深度解析 · 助益教育管理者跃迁")

if st.button("🔄 同步今日最新内参 (Sync Now)"):
    with st.spinner("Analyzing Global Data..."):
        st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for art in st.session_state.articles:
        # 爆点标题
        st.markdown(f"### 🎯 {art['punchline']}")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.markdown("#### 📘 [Read] Deep Dive")
            # 使用 info 框让文字有边界感，不散乱
            st.info(art['read'])
            
        with col2:
            st.markdown("#### 🚀 [Rise] Action Plan")
            # 使用 warning 框突出行动指令
            st.warning(art['rise'])
            
        st.markdown("---")
else:
    st.info("点击上方按钮，获取今日全球管理洞察。")
