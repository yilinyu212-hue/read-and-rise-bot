import streamlit as st
from backend import engine

st.set_page_config(page_title="Read & Rise", layout="wide")

st.markdown("""
    <style>
    .quote-box { padding: 20px; border-left: 5px solid #1E3A8A; background: #F8FAFC; margin-bottom: 15px; font-style: italic; color: #475569; }
    .source-tag { font-weight: bold; color: #64748b; font-size: 0.8rem; text-transform: uppercase; }
    .punchline { font-size: 1.6rem; font-weight: 800; color: #0F172A; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Read & Rise")

if st.button("🔄 同步全球外刊 (Force Sync)"):
    st.cache_data.clear() 
    with st.spinner("正在穿越网络获取最新真实外刊..."):
        # 这里调用的名字必须与 engine.py 里的函数名一致
        st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for art in st.session_state.articles:
        # 修正点：金句只用文字显示，绝不调用 st.image
        st.markdown(f'<div class="quote-box">“{art["golden_quote"]}”</div>', unsafe_allow_html=True)
        
        col_s1, col_s2 = st.columns([0.05, 0.95])
        with col_s1: st.image(art.get('logo', 'https://www.google.com/favicon.ico'), width=24)
        with col_s2: st.markdown(f"<span class='source-tag'>{art['source']}</span>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='punchline'>{art['punchline']}</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.6, 1], gap="large")
        with c1: st.info(art['read'])
        with c2: st.warning(art['rise'])
        st.markdown("---")
