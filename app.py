import streamlit as st
from backend import engine

st.set_page_config(page_title="Read & Rise | 高管内参", layout="wide")

st.title("🏹 Read & Rise: Global Insight for Educators")

with st.sidebar:
    st.header("控制台")
    if st.button("🔄 同步全球外刊最新内参"):
        with st.spinner("DeepSeek 正在解析..."):
            # 确保这里调用的函数名在 engine.py 中存在
            st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for art in st.session_state.articles:
        st.subheader(f"🎯 {art['punchline']}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### 📘 [Read] 深度精读")
            st.info(art['read']) # 对应 engine 里的 'read' 键
            
        with col2:
            st.markdown("#### 🚀 [Rise] 管理跃迁")
            st.warning(art['rise']) # 对应 engine 里的 'rise' 键
        st.markdown("---")
else:
    st.info("点击左侧按钮，开启今日的高管决策同步。")
