import streamlit as st
from backend import engine

st.title("🏹 Read & Rise")

if st.button("🔄 同步全球外刊 (Force Sync)"):
    st.cache_data.clear() 
    with st.spinner("正在穿越网络获取最新真实外刊..."):
        st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for art in st.session_state.articles:
        st.subheader(f"“{art['golden_quote']}”")
        st.write(f"**来源**: {art['source']} | **洞察**: {art['punchline']}")
        col1, col2 = st.columns(2)
        with col1: st.info(art['read'])
        with col2: st.warning(art['rise'])
        st.markdown("---")
