import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= 1. 页面配置 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# ================= 2. 极简 UI 样式 =================
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .welcome-text { font-size: 4.5rem; font-weight: 900; color: #0F172A; margin-top: -20px; letter-spacing: -2px; }
    .quote-card { background: #ffffff; padding: 40px; border-radius: 24px; border: 1px solid #E2E8F0; margin: 20px 0; text-align: center; }
    .book-card { background: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; transition: 0.3s; }
    .book-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
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

# ================= 4. 侧边栏导航 =================
with st.sidebar:
    st.markdown("<br><h1 style='font-size: 2rem;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Navigation", ["🏠 主页 (Home)", "🚀 今日内参 (Briefing)", "📚 精英书库 (Bookshelf)", "🧠 思维模型 (Library)", "🎙️ 英文教练 (Coaching)"], label_visibility="collapsed")

# ================= 5. 频道内容 =================

# --- 频道 0: 主页 ---
if menu == "🏠 主页 (Home)":
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.5, 1])
    
    with col_l:
        st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
        st.markdown(f"#### 📅 {datetime.now().strftime('%B %d, %Y')} | Intelligence Dashboard")
        st.markdown('<div class="quote-card"><p style="font-size:1.8rem; font-style:italic;">“The only thing worse than being blind is having sight but no vision.”</p><p>— Helen Keller</p></div>', unsafe_allow_html=True)
        
        # 主页书籍推荐（联动今日内参）
        st.subheader("📚 今日教练导读 (Recommended Reading)")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("""<div class="book-card">
                <p style='color:#64748B; font-size:0.8rem;'>MATCHED WITH TODAY'S NEWS</p>
                <h4>《The Second Curve》</h4>
                <p style='font-size:0.9rem;'>Charles Handy 著。如何在新旧时代交替中找到指数增长的转折点。</p>
            </div>""", unsafe_allow_html=True)
        with col_b2:
            st.markdown("""<div class="book-card">
                <p style='color:#64748B; font-size:0.8rem;'>STRATEGIC CLASSIC</p>
                <h4>《First Principles》</h4>
                <p style='font-size:0.9rem;'>通过 Elon Musk 的视角拆解如何回归底层物理事实。</p>
            </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown("### 📊 能力提升 (Metrics)")
        if articles:
            scores_df = pd.DataFrame([a['scores'] for a in articles if 'scores' in a]).mean().reset_index()
            st.bar_chart(scores_df.set_index('index'))

# --- 频道 1: 今日内参 (已改为折叠式排版) ---
elif menu == "🚀 今日内参 (Briefing)":
    st.header("🚀 全球商业内参")
    for art in articles:
        with st.expander(f"📌 [{art.get('source')}] {art.get('title')}"):
            c1, c2 = st.columns(2)
            with c1: st.info(art.get('en_summary'))
            with c2: st.markdown(art.get('cn_analysis'))

# --- 频道 2: 精英书库 (新增：书籍部分) ---
elif menu == "📚 精英书库 (Bookshelf)":
    st.header("📚 精英高管书库")
    st.write("不仅是书单，更是商业智慧的垂直链接。")
    st.divider()
    
    # 按照思维模型对书籍分类
    book_cat = st.tabs(["战略与变革", "领导力心理学", "技术与未来"])
    
    with book_cat[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.image("https://img9.doubanio.com/view/subject/s/public/s28325061.jpg", width=150) # 示例图
            st.subheader("《第二曲线》")
            st.write("Charles Handy 著。本书深刻探讨了企业如何在辉煌期通过‘非连续性创新’开启新的增长。")
        with col2:
            st.info("💡 **Coach Link**: 配合今日《麦肯锡报告》中提到的数字化转型章节阅读，效果最佳。")

# --- 频道 3 & 4 (保持之前的 Library 和 Coaching 代码) ---
# ... 此处省略重复的思维模型和英文教练代码 ...
