import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= 1. 页面配置 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .welcome-text { font-size: 4rem; font-weight: 900; color: #0F172A; margin-top: -20px; }
    .vocab-card { background: white; border-left: 5px solid #10416F; padding: 15px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .book-detail-card { background: white; padding: 30px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 25px; }
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据加载逻辑 =================
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, dict) and "articles" in d:
                    return d
                return {"articles": [], "books": []}
        except: return {"articles": [], "books": []}
    return {"articles": [], "books": []}

data = load_data()

# ================= 3. 导航控制 =================
with st.sidebar:
    st.markdown("<br><h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("导航菜单", ["🏠 主页", "🚀 今日内参", "📚 精读笔记", "🧠 思维模型", "🎙️ 英文教练"], label_visibility="collapsed")

# ================= 4. 各频道实现 =================

# --- 🏠 主页 ---
if menu == "🏠 主页":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.markdown(f"#### 📅 {datetime.now().strftime('%B %d, %Y')} | Insight Dashboard")
    st.markdown('<div style="background:white; padding:30px; border-radius:24px; border:1px solid #E2E8F0; margin:20px 0;"><p style="font-size:1.5rem; font-style:italic;">“The essence of strategy is choosing what not to do.”</p></div>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.subheader("📚 导读推荐 (Daily Reads)")
        if data.get("books"):
            for b in data["books"][:2]:
                st.info(f"📖 **今日推荐**: {b['book_title']} - {b['first_principle']}")
    with col_r:
        st.subheader("📊 能力雷达 (Status)")
        if data.get("articles"):
            scores_df = pd.DataFrame([a['scores'] for a in data["articles"] if 'articles' in data]).mean().reset_index()
            st.bar_chart(scores_df.set_index('index'))

# --- 🚀 今日内参 ---
elif menu == "🚀 今日内参":
    st.header("🚀 全球智库情报")
    for art in data.get("articles", []):
        with st.expander(f"📌 [{art['source']}] {art['title']}"):
            c1, c2 = st.columns(2)
            with c1: 
                st.markdown("##### 🇬🇧 Executive Summary")
                st.write(art['en_summary'])
            with c2: 
                st.markdown("##### 🇨🇳 深度解析")
                st.markdown(art['cn_analysis'])
            st.link_button("阅读原文", art['link'])

# --- 📚 精读笔记 ---
elif menu == "📚 精读笔记":
    st.header("📚 AI 深度精读笔记")
    if not data.get("books"):
        st.warning("暂无笔记，请确保 crawler 已运行。")
    else:
        for book in data["books"]:
            st.markdown(f"""
            <div class="book-detail-card">
                <h3>{book['book_title']}</h3>
                <p><strong>第一性原理:</strong> {book['first_principle']}</p>
                <p><strong>核心洞察:</strong></p>
                <ul>{"".join([f"<li>{i}</li>" for i in book['insights']])}</ul>
                <div style="background:#f0f7ff; padding:15px; border-radius:10px; color:#0d47a1;">
                    🎙️ <b>高管话术:</b> {book['executive_phrasing']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- 🧠 思维模型 ---
elif menu == "🧠 思维模型":
    st.header("🧠 商业思维模型库 (Top 10)")
    models = {
        "1. 第一性原理": "拆解事物至物理本质，重新构建。",
        "2. 第二曲线": "在巅峰开启新增长引擎。",
        "3. 飞轮效应": "建立自我强化的正向循环。",
        "4. 边际安全": "为决策保留容错空间。",
        "5. 帕累托法则": "聚焦产生 80% 收益的 20% 投入。",
        "6. 复利效应": "长期的指数级价值叠加。",
        "7. 机会成本": "衡量放弃的最高价值。",
        "8. 反脆弱": "从波动和随机性中获益。",
        "9. 胜任力圈": "专注于真正理解的领域。",
        "10. 沉没成本误区": "理性决策应关注未来。"
    }
    col1, col2 = st.columns(2)
    for i, (m_name, m_desc) in enumerate(models.items()):
        target = col1 if i % 2 == 0 else col2
        with target.expander(m_name):
            st.write(m_desc)
            # 修复了截图中的 IndentationError
            if "飞轮效应" in m_name:
                st.info("💡 建议结合《从优秀到卓越》阅读。")
            if "第二曲线" in m_name:
                st.info("💡 建议在企业利润最高时开始布局新业务。")
    
# --- 🎙️ 英文教练 ---
elif menu == "🎙️ 英文教练":
    st.header("🎙️ 英文教练：高阶表达卡片")
    all_vocab = {}
    for a in data.get("articles", []): all_vocab.update(a.get('vocabulary', {}))
    
    # 彻底解决排版拥挤问题
    v_col1, v_col2 = st.columns(2)
    for i, (word, mean) in enumerate(all_vocab.items()):
        target = v_col1 if i % 2 == 0 else v_col2
        target.markdown(f'<div class="vocab-card"><b style="font-size:1.1rem;">{word}</b><br><span style="color:#64748B;">{mean}</span></div>', unsafe_allow_html=True)
