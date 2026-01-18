import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go

# ================= 1. 样式配置 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .coach-card { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px; border-left: 8px solid #38BDF8; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .tag { background: #E0F2FE; color: #0369A1; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-right: 8px; }
    .en-sub { color: #94A3B8; font-style: italic; font-size: 0.9rem; margin-bottom: 5px; }
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
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', line_color='#38BDF8', fillcolor='rgba(56, 189, 248, 0.3)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350, margin=dict(l=40, r=40, t=20, b=20))
    return fig

# ================= 3. 频道逻辑 =================
with st.sidebar:
    st.markdown("<h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("导航", ["🏠 主页 Dashboard", "🚀 今日内参 Insights", "📚 精读笔记 Books", "🧠 思维模型 Models", "🎙️ 英文教练 Coach"], label_visibility="collapsed")
    st.markdown(f"<div style='margin-top:200px; opacity:0.5; font-size:0.8rem;'>Updated: {data.get('update_time', 'N/A')}</div>", unsafe_allow_html=True)

# --- 🏠 主页 ---
if menu == "🏠 主页 Dashboard":
    # 中英双语提问看板
    st.markdown(f"""
    <div class="coach-card">
        <h4 style="color: #38BDF8; margin: 0; letter-spacing: 1px;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size: 1.1rem; margin-top: 15px; color: #94A3B8; font-style: italic;">“{data.get('weekly_question_en', 'How do you balance short-term performance with long-term strategy?')}”</p>
        <p style="font-size: 1.4rem; font-weight: 500; margin-top: 5px;">“{data.get('weekly_question_cn', '你如何在短期业绩与长期战略之间取得平衡？')}”</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1.6, 1])
    with col_l:
        st.subheader("💡 知识联动建议 / Linked Insight")
        if data.get("articles"):
            top = data["articles"][0]
            st.markdown(f"""
            <div class="card">
                <p class="en-sub">Based on: {top['title']}</p>
                <p><b>今日深度分析：</b>{top['title']}</p>
                <span class="tag">🧠 {top.get('related_model', 'First Principles')}</span>
                <span class="tag">📚 {top.get('related_book', 'Principles')}</span>
            </div>
            """, unsafe_allow_html=True)
    with col_r:
        st.subheader("📊 领导力雷达 / Competency")
        if data.get("articles"):
            avg_scores = pd.DataFrame([a['scores'] for a in data["articles"]]).mean().to_dict()
            st.plotly_chart(draw_radar(avg_scores), use_container_width=True)

# --- 🚀 今日内参 ---
elif menu == "🚀 今日内参 Insights":
    st.header("🚀 Global Business Insights")
    for art in data.get("articles", []):
        with st.expander(f"📌 [{art['source']}] {art['title']}"):
            st.markdown(f"<span class='tag'>Model: {art.get('related_model')}</span> <span class='tag'>Reading: {art.get('related_book')}</span>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.info(art['en_summary'])
            c2.markdown(art['cn_analysis'])
            st.link_button("Original Link / 阅读原文", art['link'])

# --- 📚 精读笔记 ---
elif menu == "📚 精读笔记 Books":
    st.header("📚 Executive Book Summaries")
    for book in data.get("books", []):
        with st.expander(f"📖 {book['book_title']}"):
            st.markdown(f"**First Principle / 核心逻辑:** {book['first_principle']}")
            for ins in book['insights']: st.markdown(f"- {ins}")
            st.success(f"🎙️ **Executive Phrasing / 高管话术:** {book['executive_phrasing']}")

# --- 🧠 思维模型 ---
elif menu == "🧠 思维模型 Models":
    st.header("🧠 Mental Models for Leaders")
    models = {
        "第一性原理 First Principles": "回归事物本质，重新构建。",
        "第二曲线 Second Curve": "在现有业务巅峰前开启新增长点。",
        "飞轮效应 Flywheel Effect": "建立正向循环，实现自动加速。"
    }
    cols = st.columns(2)
    for i, (name, desc) in enumerate(models.items()):
        with cols[i % 2].expander(name):
            st.write(desc)
            if "飞轮效应" in name:
                st.info("💡 Identify factors that push each other in a loop.")
                
            if "第二曲线" in name:
                st.info("💡 Strategic pivot before the first curve declines.")
                

# --- 🎙️ 英文教练 ---
elif menu == "🎙️ 英文教练 Coach":
    st.header("🎙️ Executive Vocabulary")
    all_v = {}
    for a in data.get("articles", []): all_v.update(a.get('vocabulary', {}))
    v_cols = st.columns(3)
    for i, (w, m) in enumerate(all_v.items()):
        v_cols[i % 3].markdown(f'<div class="card"><b>{w}</b><br><small>{m}</small></div>', unsafe_allow_html=True)
