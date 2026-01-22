import streamlit as st
from backend import engine

st.set_page_config(page_title="Read & Rise", layout="wide")

# 引入呼吸感 CSS
st.markdown("""
    <style>
    .stMarkdown { line-height: 1.8; color: #334155; }
    .quote-box { 
        padding: 25px; 
        border-left: 5px solid #1E3A8A; 
        background: #F1F5F9; 
        margin-bottom: 20px;
        font-style: italic;
    }
    h3 { margin-top: 2rem !important; color: #0F172A; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Read & Rise")
st.caption("跨界全球洞察 · 赋能管理决策 | Global Intelligence for Decision Makers")

if st.button("🔄 同步全球商业内参 (Sync Insight)"):
    with st.spinner("DeepSeek 正在扫描全球动态..."):
        st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for art in st.session_state.articles:
        # 1. 社交金句卡片
        st.markdown(f"""<div class="quote-box">“{art['golden_quote']}”</div>""", unsafe_allow_html=True)
        
        # 2. 深度爆点
        st.markdown(f"### 🎯 {art['punchline']}")
        
        # 3. 三段式展示
        col1, col2 = st.columns([1.5, 1], gap="large")
        with col1:
            st.info(art['read'])
        with col2:
            st.success(art['rise'])
        st.markdown("<br><hr>", unsafe_allow_html=True)
else:
    st.info("点击按钮，获取今日全球商业与管理趋势拆解。")
