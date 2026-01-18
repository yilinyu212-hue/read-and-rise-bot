import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= 1. 页面配置 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# ================= 2. 深度样式定制 (解决排版拥挤) =================
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    /* 主页大标题 */
    .welcome-text { font-size: 4rem; font-weight: 900; color: #0F172A; margin-top: -20px; }
    
    /* 书籍卡片样式 */
    .book-container {
        display: flex;
        gap: 20px;
        overflow-x: auto;
        padding: 10px 0;
    }
    .book-card {
        flex: 0 0 300px;
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .book-title { font-size: 1.2rem; font-weight: bold; color: #1E293B; margin-bottom: 5px; }
    .book-author { color: #64748B; font-size: 0.9rem; margin-bottom: 15px; }
    
    /* 词汇卡片样式 */
    .vocab-card {
        background: #ffffff;
        border-left: 5px solid #10416F;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .vocab-word { font-family: 'Courier New', monospace; font-weight: bold; color: #10416F; font-size: 1.1rem; }
    .vocab-mean { color: #475569; font-size: 0.95rem; }

    /* 侧边栏 */
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. 数据加载 =================
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

articles = load_data()

# ================= 4. 侧边栏 =================
with st.sidebar:
    st.markdown("<br><h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("Navigation", ["🏠 主页 (Home)", "🚀 今日内参 (Briefing)", "📚 精英书库 (Bookshelf)", "🧠 思维模型 (Library)", "🎙️ 英文教练 (Coaching)"], label_visibility="collapsed")

# ================= 5. 频道内容 =================

# --- 频道 0: 主页 (干净排版) ---
if menu == "🏠 主页 (Home)":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.markdown(f"#### 📅 {datetime.now().strftime('%B %d, %Y')} | Intelligence Dashboard")
    
    st.markdown('<div style="background:white; padding:30px; border-radius:24px; border:1px solid #E2E8F0; margin:20px 0;"><p style="font-size:1.5rem; font-style:italic; color:#334155;">“Strategy is about making choices, trade-offs; it\'s about deliberately choosing to be different.”</p><p align="right">— Michael Porter</p></div>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.subheader("📚 推荐导读 (Featured Books)")
        # 即使数据没更新，主页也先展示几个固定的
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="book-card"><p class="book-title">《The Second Curve》</p><p class="book-author">Charles Handy</p><p>探索企业与个人如何跨越非连续性增长。</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="book-card"><p class="book-title">《Principles》</p><p class="book-author">Ray Dalio</p><p>瑞·达利欧关于应对复杂世界的算法总结。</p></div>', unsafe_allow_html=True)
    with col_r:
        st.subheader("📊 能力图谱")
        if articles:
            scores_df = pd.DataFrame([a['scores'] for a in articles if 'scores' in a]).mean().reset_index()
            st.bar_chart(scores_df.set_index('index'))

# --- 频道 1: 今日内参 ---
elif menu == "🚀 今日内参 (Briefing)":
    st.header("🚀 全球商业内参")
    if not articles:
        st.info("数据同步中...")
    else:
        for art in articles:
            with st.expander(f"📌 [{art.get('source')}] {art.get('title')}"):
                c1, c2 = st.columns(2)
                with c1: 
                    st.markdown("##### 🇬🇧 Summary")
                    st.write(art.get('en_summary'))
                with c2: 
                    st.markdown("##### 🇨🇳 深度拆解")
                    st.markdown(art.get('cn_analysis'))

# --- 频道 2: 精英书库 ---
elif menu == "📚 精英书库 (Bookshelf)":
    st.header("📚 精英高管书库")
    st.write("将碎片资讯转化为系统认知的“压舱石”。")
    st.divider()
    
    # 模拟书库排版
    books = [
        {"t": "High Output Management", "a": "Andrew Grove", "d": "英特尔传奇 CEO 格鲁夫的管理圣经。"},
        {"t": "Zero to One", "a": "Peter Thiel", "d": "关于创新与垄断的底层思考。"},
        {"t": "The Lean Startup", "a": "Eric Ries", "d": "在极度不确定性中快速迭代。"}
    ]
    
    # 每行放 3 本书，增加间距
    for i in range(0, len(books), 3):
        cols = st.columns(3)
        for j, book in enumerate(books[i:i+3]):
            with cols[j]:
                st.markdown(f"""
                <div class="book-card">
                    <p class="book-title">{book['t']}</p>
                    <p class="book-author">{book['a']}</p>
                    <p style="font-size:0.9rem;">{book['d']}</p>
                </div>
                """, unsafe_allow_html=True)

# --- 频道 3: 英文教练 (彻底修复排版) ---
elif menu == "🎙️ 英文教练 (Coaching)":
    st.header("🎙️ 英文教练频道")
    st.write("提升在国际董事会上的沟通魅力。")
    st.divider()
    
    if articles:
        all_vocab = {}
        for a in articles: all_vocab.update(a.get('vocabulary', {}))
        
        # 改为垂直卡片流，不再并排挤压
        col_v1, col_v2 = st.columns(2)
        for i, (word, mean) in enumerate(all_vocab.items()):
            target_col = col_v1 if i % 2 == 0 else col_v2
            target_col.markdown(f"""
                <div class="vocab-card">
                    <div class="vocab-word">{word}</div>
                    <div class="vocab-mean">{mean}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("今日词汇正在同步中...")
