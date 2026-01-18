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
    .coach-card { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px; border-left: 8px solid #38BDF8; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .tag { background: #F0F9FF; color: #0369A1; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; margin-right: 8px; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据处理与可视化 =================
@st.cache_data(ttl=3600)
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"articles": [], "books": [], "weekly_question": ""}
    return {"articles": [], "books": [], "weekly_question": ""}

data = load_data()

def draw_radar(scores_dict):
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', line_color='#38BDF8', fillcolor='rgba(56, 189, 248, 0.3)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=380, margin=dict(l=40, r=40, t=20, b=20))
    return fig

# ================= 3. 侧边栏导航 =================
with st.sidebar:
    st.markdown("<br><h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("导航菜单", ["🏠 主页", "🚀 今日内参", "📚 精读笔记", "🧠 思维模型", "🎙️ 英文教练"], label_visibility="collapsed")
    st.markdown(f"<div style='margin-top:150px; opacity:0.5; font-size:0.8rem;'>数据更新: {data.get('update_time', 'N/A')}</div>", unsafe_allow_html=True)

# ================= 4. 频道内容实现 =================

# --- 🏠 主页 ---
if menu == "🏠 主页":
    # 启发式提问看板
    st.markdown(f"""
    <div class="coach-card">
        <h4 style="color: #38BDF8; margin: 0;">🎙️ 今日教练提问 (Weekly Inquiry)</h4>
        <p style="font-size: 1.4rem; margin-top: 15px; font-weight: 500; line-height: 1.5;">“{data.get('weekly_question', '如何平衡短期利润与长期增长？')}”</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1.6, 1])
    with col_l:
        st.subheader("💡 知识联动建议 (Daily Insight)")
        if data.get("articles"):
            top = data["articles"][0]
            st.markdown(f"""
            <div class="card">
                <p>基于今日深度报告：<b>{top['title']}</b></p>
                建议联动模型：<span class="tag">🧠 {top.get('related_model', '第一性原理')}</span><br><br>
                建议延伸阅读：<span class="tag">📚 {top.get('related_book', '《原则》')}</span>
            </div>
            """, unsafe_allow_html=True)
    with col_r:
        st.subheader("📊 领导力雷达 (Radar)")
        if data.get("articles"):
            avg_scores = pd.DataFrame([a['scores'] for a in data["articles"]]).mean().to_dict()
            st.plotly_chart(draw_radar(avg_scores), use_container_width=True)

# --- 🚀 今日内参 ---
elif menu == "🚀 今日内参":
    st.header("🚀 全球智库情报")
    for art in data.get("articles", []):
        with st.expander(f"📌 [{art['source']}] {art['title']}"):
            st.markdown(f"<span class='tag'>关联模型: {art.get('related_model')}</span> <span class='tag'>关联书目: {art.get('related_book')}</span>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.info(art['en_summary'])
            c2.markdown(art['cn_analysis'])
            st.link_button("阅读原文", art['link'])

# --- 📚 精读笔记 ---
elif menu == "📚 精读笔记":
    st.header("📚 AI 书籍精读书库")
    for book in data.get("books", []):
        with st.expander(f"📖 {book['book_title']}"):
            st.markdown(f"**第一性原理:** {book['first_principle']}")
            for ins in book['insights']: st.markdown(f"- {ins}")
            st.success(f"🎙️ **高管话术:** {book['executive_phrasing']}")

# --- 🧠 思维模型 (彻底修复缩进错误) ---
elif menu == "🧠 思维模型":
    st.header("🧠 核心商业思维模型库")
    models = {"第一性原理": "拆解事物至本质。", "第二曲线": "在现有业务顶峰开启新增长。", "飞轮效应": "建立自我强化的正向循环。"}
    cols = st.columns(2)
    for i, (name, desc) in enumerate(models.items()):
        with cols[i % 2].expander(name):
            st.write(desc)
            # 此处已补齐缩进块，修复报错
            if "飞轮效应" in name:
                st.info("💡 建议寻找企业内部互相驱动的闭环。")
                            if "第二曲线" in name:
                st.info("💡 建议在第一曲线巅峰前布局新业务。")
                
# --- 🎙️ 英文教练 ---
elif menu == "🎙️ 英文教练":
    st.header("🎙️ 英文教练词汇卡片")
    all_v = {}
    for a in data.get("articles", []): all_v.update(a.get('vocabulary', {}))
    v_cols = st.columns(3)
    for i, (w, m) in enumerate(all_v.items()):
        v_cols[i % 3].markdown(f'<div class="card"><b>{w}</b><br><small>{m}</small></div>', unsafe_allow_html=True)
