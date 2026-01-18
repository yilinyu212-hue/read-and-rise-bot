import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
from datetime import datetime

# ================= 1. 页面设置与样式 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .welcome-text { font-size: 3.5rem; font-weight: 900; color: #0F172A; margin-top: -30px; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .tag { background: #E0F2FE; color: #0369A1; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据处理与缓存 =================
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

# ================= 3. 导航 =================
with st.sidebar:
    st.markdown("<br><h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("MENU", ["🏠 主页", "🚀 今日内参", "📚 精读笔记", "🧠 思维模型", "🎙️ 英文教练"], label_visibility="collapsed")
    st.markdown(f"<div style='margin-top:200px; opacity:0.5; font-size:0.7rem;'>Last Sync: {data.get('update_time', 'N/A')}</div>", unsafe_allow_html=True)

# ================= 4. 频道内容 =================

# --- 主页 (首页仪表盘) ---
if menu == "🏠 主页":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.6, 1])
    with col_l:
        st.markdown('<div class="card" style="border-left: 8px solid #10416F;"><h4>今日教练金句</h4><p style="font-size:1.4rem; font-style:italic;">“Complexity is your enemy. Any fool can make something complicated. It is hard to keep things simple.”</p><p>— Richard Branson</p></div>', unsafe_allow_html=True)
        st.subheader("💡 知识联动建议 (Linked Insight)")
        if data.get("articles"):
            latest = data["articles"][0]
            st.markdown(f"""
            <div class="card">
                <p>根据今日热点：<b>{latest['title'][:50]}...</b></p>
                建议联动学习模型：<span class="tag">{latest.get('related_model', '第一性原理')}</span><br><br>
                深度阅读推荐：<span class="tag">{latest.get('recommended_book', '《原则》')}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.subheader("📊 能力平衡图 (Radar)")
        if data.get("articles"):
            avg_scores = pd.DataFrame([a['scores'] for a in data["articles"]]).mean().to_dict()
            st.plotly_chart(draw_radar(avg_scores), use_container_width=True)

# --- 今日内参 (外刊) ---
elif menu == "🚀 今日内参":
    st.header("🚀 全球商业内参")
    for art in data.get("articles", []):
        with st.expander(f"📌 [{art['source']}] {art['title']}"):
            st.markdown(f"<span class='tag'>关联模型: {art.get('related_model')}</span> <span class='tag'>推荐书目: {art.get('recommended_book')}</span>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.info(art['en_summary'])
            with c2: st.markdown(art['cn_analysis'])
            st.link_button("阅读原文", art['link'])

# --- 精读笔记 (书籍) ---
elif menu == "📚 精读笔记":
    st.header("📚 AI 精读书库")
    for book in data.get("books", []):
        with st.expander(f"📖 {book['book_title']}"):
            st.markdown(f"**核心逻辑:** {book['first_principle']}")
            st.write("**战略洞察:**")
            for ins in book['insights']: st.markdown(f"- {ins}")
            st.success(f"🎙️ **高管会议表达:** {book['executive_phrasing']}")

# --- 思维模型 (库) ---
elif menu == "🧠 思维模型":
    st.header("🧠 商业思维模型库")
    models = {
        "第一性原理": "回归物理本质。", "第二曲线": "跨越非连续性增长。",
        "飞轮效应": "正向循环自动加速。", "边际安全": "决策容错储备。",
        "帕累托法则": "聚焦核心 20%。", "复利效应": "长期指数增长。",
        "机会成本": "衡量放弃的价值。", "反脆弱": "从波动中受益。",
        "胜任力圈": "专注擅长领域。", "均值回归": "周期理性预期。"
    }
    col1, col2 = st.columns(2)
    for i, (name, desc) in enumerate(models.items()):
        target = col1 if i % 2 == 0 else col2
        with target.expander(name):
            st.write(desc)
            if "第二曲线" in name:
                

# --- 英文教练 ---
elif menu == "🎙️ 英文教练":
    st.header("🎙️ 英文教练词汇卡")
    all_v = {}
    for a in data.get("articles", []): all_v.update(a.get('vocabulary', {}))
    cols = st.columns(2)
    for i, (w, m) in enumerate(all_v.items()):
        cols[i % 2].markdown(f'<div class="card"><b>{w}</b><br><small>{m}</small></div>', unsafe_allow_html=True)
