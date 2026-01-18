import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= 1. 页面配置与视觉优化 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .welcome-text { font-size: 4rem; font-weight: 900; color: #0F172A; margin-top: -20px; }
    .quote-card { background: white; padding: 30px; border-radius: 24px; border: 1px solid #E2E8F0; margin: 20px 0; }
    .vocab-card { background: white; border-left: 5px solid #10416F; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .book-box { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据处理 =================
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                d = json.load(f)
                return d if isinstance(d, dict) else {"articles": [], "books": []}
        except: return {"articles": [], "books": []}
    return {"articles": [], "books": []}

data = load_data()

# ================= 3. 侧边栏导航 =================
with st.sidebar:
    st.markdown("<br><h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("导航", ["🏠 主页", "🚀 今日内参", "📚 精读笔记", "🧠 思维模型", "🎙️ 英文教练"], label_visibility="collapsed")

# ================= 4. 各频道实现 =================

# --- 🏠 主页 ---
if menu == "🏠 主页":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.markdown(f"#### 📅 {datetime.now().strftime('%B %d, %Y')} | Insight Dashboard")
    st.markdown('<div class="quote-card"><p style="font-size:1.5rem; font-style:italic; color:#334155;">“The best way to predict the future is to create it.”</p></div>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.subheader("📚 导读推荐 (Daily Picks)")
        if data["books"]:
            for b in data["books"][:2]:
                st.markdown(f'<div class="book-box"><b>{b["book_title"]}</b><br><small>{b["first_principle"]}</small></div>', unsafe_allow_html=True)
    with col_r:
        st.subheader("📊 综合能力值")
        if data["articles"]:
            scores_df = pd.DataFrame([a['scores'] for a in data["articles"] if 'scores' in a]).mean().reset_index()
            st.bar_chart(scores_df.set_index('index'))

# --- 🚀 今日内参 ---
elif menu == "🚀 今日内参":
    st.header("🚀 全球智库情报")
    for art in data["articles"]:
        with st.expander(f"📌 [{art['source']}] {art['title']}"):
            c1, c2 = st.columns(2)
            with c1: st.info(art['en_summary'])
            with c2: st.markdown(art['cn_analysis'])
            st.link_button("View Original", art['link'])

# --- 📚 精读笔记 ---
elif menu == "📚 精读笔记":
    st.header("📚 AI 书籍精读笔记")
    for book in data["books"]:
        with st.expander(f"📖 {book['book_title']}", expanded=True):
            st.markdown(f"**核心第一性原理:** {book['first_principle']}")
            st.markdown("**关键洞察:**")
            for ins in book['insights']: st.markdown(f"- {ins}")
            st.success(f"🎙️ **高管会议表达:** {book['executive_phrasing']}")

# --- 🧠 思维模型 ---
elif menu == "🧠 思维模型":
    st.header("🧠 商业思维模型库 (Top 10)")
    models = {
        "1. 第一性原理": "拆解至物理本质。", "2. 第二曲线": "在巅峰开启新增长。",
        "3. 飞轮效应": "良性循环的自动加速。", "4. 边际安全": "容错空间的保护。",
        "5. 帕累托法则": "聚焦核心 20%。", "6. 复利效应": "长期价值的指数级增长。",
        "7. 机会成本": "衡量放弃的最高价值。", "8. 反脆弱": "从波动中受益。",
        "9. 胜任力圈": "在擅长领域深耕。", "10. 均值回归": "周期性的理性预期。"
    }
    col1, col2 = st.columns(2)
    for i, (m_name, m_desc) in enumerate(models.items()):
        target = col1 if i % 2 == 0 else col2
        with target.expander(m_name):
            st.write(m_desc)
            if "第二曲线" in m_name:
                
            if "飞轮效应" in m_name:
                

# --- 🎙️ 英文教练 ---
elif menu == "🎙️ 英文教练":
    st.header("🎙️ 英文教练：词汇卡片")
    all_v = {}
    for a in data["articles"]: all_v.update(a.get('vocabulary', {}))
    v_c1, v_c2 = st.columns(2)
    for i, (w, m) in enumerate(all_v.items()):
        target = v_c1 if i % 2 == 0 else v_c2
        target.markdown(f'<div class="vocab-card"><b>{w}</b><br><small>{m}</small></div>', unsafe_allow_html=True)
