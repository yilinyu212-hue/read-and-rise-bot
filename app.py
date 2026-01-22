import streamlit as st
from backend import engine

st.set_page_config(page_title="Read & Rise", layout="wide")

# CSS：打造内参报纸感
st.markdown("""
    <style>
    .source-header { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
    .source-name { font-weight: bold; color: #475569; text-transform: uppercase; font-size: 0.85rem; }
    .quote-card { border-left: 4px solid #1E3A8A; padding: 15px; background: #F8FAFC; margin: 15px 0; font-style: italic; }
    .punchline { font-size: 1.5rem; font-weight: 800; color: #0F172A; line-height: 1.3; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Read & Rise")
st.caption("全球顶级外刊实时拆解 | Global Intel for Decision Makers")

if st.button("🔄 同步全球外刊 (Sync Global Intelligence)"):
    with st.spinner("正在从 HBR, Economist, MIT 等顶级渠道同步..."):
        st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for art in st.session_state.articles:
        with st.container():
            # 1. 呈现外刊来源 (The Source)
            st.markdown(f"""
                <div class="source-header">
                    <img src="{art['logo']}" width="20">
                    <span class="source-name">{art['source']}</span>
                    <a href="{art['url']}" style="font-size: 0.7rem; color: #3b82f6;">READ ORIGINAL ↗</a>
                </div>
            """, unsafe_allow_html=True)
            
            # 2. 深度标题与爆点
            st.markdown(f"<div class='punchline'>{art['punchline']}</div>", unsafe_allow_html=True)
            
            # 3. 三段式：中英对照 + 决策行动
            col1, col2 = st.columns([1.6, 1], gap="large")
            with col1:
                st.info(art['read'])
            with col2:
                st.warning(art['rise'])
            st.markdown("---")
else:
    st.info("点击上方按钮，同步来自全球顶级商业、科技智库的最新内参。")
