import streamlit as st
from backend import engine
import io
from PIL import Image, ImageDraw, ImageFont # 确保你安装了 Pillow 库
import base64

# --- 配置页面 ---
st.set_page_config(page_title="Read & Rise", layout="wide")

# --- CSS 样式 ---
st.markdown("""
    <style>
    .quote-box { padding: 20px; border-left: 5px solid #1E3A8A; background: #F8FAFC; margin-bottom: 15px; font-style: italic; color: #475569; }
    .source-tag { font-weight: bold; color: #64748b; font-size: 0.8rem; text-transform: uppercase; }
    .punchline { font-size: 1.6rem; font-weight: 800; color: #0F172A; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Read & Rise")
st.caption("全球顶级外刊实时拆解 · 跨界决策内参")

if st.button("🔄 同步全球外刊 (Sync Global Intel)"):
    with st.spinner("正在解析全球智库数据..."):
        st.session_state.articles = engine.sync_global_publications()

if "articles" in st.session_state:
    for i, art in enumerate(st.session_state.articles):
        # 1. 社交金句卡片
        st.markdown(f'<div class="quote-box">“{art["golden_quote"]}”</div>', unsafe_allow_html=True)
        
        # --- 新增功能：一键生成分享海报 ---
        if st.button(f"✨ 生成金句海报 (Share Insight) {i}"):
            # 触发图像生成
            st.image(art["golden_quote"])
            
        # 2. 报头 (Logo + 来源)
        col_s1, col_s2 = st.columns([0.05, 0.95])
        with col_s1: st.image(art['logo'], width=24)
        with col_s2: st.markdown(f"<span class='source-tag'>{art['source']}</span>", unsafe_allow_html=True)
        
        # 3. 爆点与拆解
        st.markdown(f"<div class='punchline'>{art['punchline']}</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.6, 1], gap="large")
        with c1: st.info(art['read'])
        with c2: st.warning(art['rise'])
        st.markdown("---")
