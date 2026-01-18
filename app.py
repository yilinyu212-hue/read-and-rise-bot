import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
from datetime import datetime

# ================= 1. 样式与配置 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .tag { background: #E0F2FE; color: #0369A1; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .vocab-card { background: white; border-left: 5px solid #10416F; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据处理 =================
@st.cache_data(ttl=3600)
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"articles": [], "books": []}
    return {"articles": [], "books": []}

data = load_data()

def draw_radar(scores_dict):
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', line_color='#10416F'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350, margin=dict(l=40, r=40, t=20, b=20))
    return fig

# ================= 3. 导航与频道 =================
with st.sidebar:
    st.markdown("<br><h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("MENU", ["🏠 主页", "🚀 今日内参", "📚 精读笔记", "🧠 思维模型", "🎙️ 英文教练"], label_visibility="collapsed")

# --- 🏠 主页 ---
if menu == "🏠 主页":
    st.markdown("### Hi, Leaders! 👋")
    col_l, col_r = st.columns([1.6, 1])
    with col_l:
        st.markdown('<div class="card">“The essence of strategy is choosing what not to do.”</div>', unsafe_allow_html=True)
        if data.get("books"):
            for b in data["books"][:2]:
                st.info(f"📖 **今日推荐**: {b['book_title']} - {b['first_principle'][:100]}...")
    with col_r:
        if data.get("articles"):
            avg_scores = pd.DataFrame([a['scores'] for a in data["articles"]]).mean().to_dict()
            st.plotly_chart(draw_radar(avg_scores), use_container_width=True)

# --- 🚀 今日内参 ---
elif menu == "🚀 今日内参":
    st.header("🚀 全球智库内参")
    for art in data.get("articles", []):
        with st.expander(f"📌 [{art['source']}] {art['title']}"):
            st.markdown(f"<span class='tag'>关联模型: {art.get('related_model')}</span>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.info(art['en_summary'])
            c2.markdown(art['cn_analysis'])
            st.link_button("View Original", art['link'])

# --- 📚 精读笔记 ---
elif menu == "📚 精读笔记":
    st.header("📚 AI 书籍精读笔记")
    for book in data.get("books", []):
        with st.expander(f"📖 {book['book_title']}", expanded=True):
            st.markdown(f"**核心逻辑:** {book['first_principle']}")
            for ins in book['insights']: st.markdown(f"- {ins}")
            st.success(f"🎙️ **高管表达:** {book['executive_phrasing']}")

# --- 🧠 思维模型 (修复缩进错误) ---
elif menu == "🧠 思维模型":
    st.header("🧠 核心商业思维模型")
    models = {"第一性原理": "回归物理事实。", "第二曲线": "在巅峰开启新增长。", "飞轮效应": "正向循环自动加速。"}
    cols = st.columns(2)
    for i, (name, desc) in enumerate(models.items()):
        with cols[i % 2].expander(name):
            st.write(desc)
            # 关键：确保 if 块内有缩进代码
            if "飞轮效应" in name:
                st.info("💡 建议结合《从优秀到卓越》应用。")
                
# --- 🎙️ 英文教练 (优化排版) ---
elif menu == "🎙️ 英文教练":
    st.header("🎙️ 英文教练：高阶表达卡片")
    all_vocab = {}
    for a in data.get("articles", []): all_vocab.update(a.get('vocabulary', {}))
    v_cols = st.columns(3) # 改为三列排版，解决拥挤
    for i, (w, m) in enumerate(all_vocab.items()):
        v_cols[i % 3].markdown(f'<div class="vocab-card"><b>{w}</b><br><small>{m}</small></div>', unsafe_allow_html=True)
