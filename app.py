import streamlit as st
from backend import engine

st.set_page_config(page_title="Read & Rise | Global Insight", layout="wide")

# 自定义 CSS：增加留白，让内容不再密集
st.markdown("""
    <style>
    .stMarkdown { line-height: 1.8; letter-spacing: 0.02rem; }
    h3 { color: #1E3A8A; padding-top: 1rem; }
    .report-box { padding: 20px; border-radius: 10px; background-color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Read & Rise")
st.caption("跨界全球洞察 · 赋能管理决策 | Global Intelligence for Decision Makers")

if st.button("🔄 同步全球商业内参 (Sync Insight)"):
    with st.spinner("DeepSeek 正在解析全球战略数据..."):
        st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for art in st.session_state.articles:
        # 核心爆点
        st.markdown(f"### 🎯 {art['punchline']}")
        
        col1, col2 = st.columns([3, 2], gap="large")
        
        with col1:
            st.markdown("#### 📘 [Read] 逻辑拆解")
            st.info(art['read'])
            
        with col2:
            st.markdown("#### 🚀 [Rise] 跃迁行动")
            st.warning(art['rise'])
        st.markdown("---")
else:
    st.write("点击按钮，获取今日全球商业与管理趋势拆解。")
