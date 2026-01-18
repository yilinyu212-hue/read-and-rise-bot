import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= 1. 极简页面配置 =================
st.set_page_config(
    page_title="Read & Rise",
    layout="wide",
    page_icon="🏹",
    initial_sidebar_state="expanded"
)

# ================= 2. 干净的 CSS 样式表 =================
st.markdown("""
    <style>
    /* 全局背景色调：浅灰蓝，极具现代感 */
    .stApp { background-color: #F8FAFC; }
    
    /* 主标题：Hi Leaders */
    .welcome-text { 
        font-size: 4.5rem; 
        font-weight: 900; 
        color: #0F172A; 
        margin-top: -20px;
        letter-spacing: -2px;
    }
    
    /* 今日金句盒子 */
    .quote-card {
        background: #ffffff;
        padding: 40px;
        border-radius: 24px;
        border: 1px solid #E2E8F0;
        margin: 20px 0;
        text-align: center;
    }
    .quote-text {
        font-size: 1.8rem;
        font-style: italic;
        color: #334155;
        line-height: 1.6;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }

    /* 隐藏 Streamlit 默认装饰 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ================= 3. 数据处理 =================
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
    st.markdown("<p style='opacity: 0.7;'>Executive Coaching Platform</p>", unsafe_allow_html=True)
    st.divider()
    
    # 清爽的导航菜单
    menu = st.radio(
        "Navigation",
        ["🏠 主页 (Home)", "🚀 今日内参 (Briefing)", "🧠 思维模型 (Library)", "🎙️ 英文教练 (Coaching)"],
        label_visibility="collapsed"
    )
    
    st.spacer = st.markdown("<br>" * 10, unsafe_allow_html=True)
    st.caption("Intelligence status: Active")

# ================= 5. 频道内容实现 =================

# --- 频道 0: 极简主页 (The Dashboard) ---
if menu == "🏠 主页 (Home)":
    # 顶部留白
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.5, 1])
    
    with col_l:
        st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
        st.markdown(f"#### 📅 {datetime.now().strftime('%B %d, %Y')} | Insight for the Modern Executive")
        
        # 今日金句 - 核心视觉中心
        st.markdown(f"""
            <div class="quote-card">
                <p class="quote-text">“The essence of strategy is choosing what not to do.”</p>
                <p style="color: #64748B; margin-top: 20px;">— Michael Porter</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.success("**Coach Advice**: Today's global feed suggests a focus on 'Decision Resilience' due to market volatility.")

    with col_r:
        st.markdown("### 📊 能力提升看板 (Growth Radar)")
        if articles:
            scores_list = [a['scores'] for a in articles if 'scores' in a]
            if scores_list:
                df = pd.DataFrame(scores_list).mean().reset_index()
                df.columns = ['Dimension', 'Strength']
                # 使用更加高级的水平条形图或雷达图感
                st.bar_chart(df.set_index('Dimension'))
        else:
            st.info("Waiting for data sync...")

# --- 频道 1: 今日内参 (Briefing) ---
elif menu == "🚀 今日内参 (Briefing)":
    st.header("🚀 全球商业内参")
    st.write("已同步来自 HBR, McKinsey, MIT 等 12 个顶级智库的最新解析。")
    st.divider()
    
    if not articles:
        st.warning("Data is being analyzed. Please check Actions.")
    else:
        for art in articles:
            with st.expander(f"📌 {art.get('source')} : {art.get('title')}", expanded=False):
                col_en, col_cn = st.columns(2)
                with col_en:
                    st.markdown("##### 🇬🇧 Executive Summary")
                    st.info(art.get('en_summary'))
                with col_cn:
                    st.markdown("##### 🇨🇳 商业教练拆解")
                    st.markdown(art.get('cn_analysis'))
                st.link_button("Read Original Article", art.get('link'))

# --- 频道 2: 思维模型 (Library) ---
elif menu == "🧠 思维模型 (Library)":
    st.header("🧠 核心思维模型")
    st.write("构建您的商业决策底层操作系统。")
    
    model = st.selectbox("Select Model", ["第二曲线", "第一性原理"])
    
    if model == "第二曲线":
        st.graphviz_chart('digraph { node[fontname="SimHei",shape=box] "第二曲线" -> {"第一曲线"; "创新期"; "爆发期"} }')
    else:
        st.graphviz_chart('digraph { node[fontname="SimHei",shape=ellipse] "第一性原理" -> "原子事实" -> "重新构建" }')

# --- 频道 3: 英文教练 (Coaching) ---
elif menu == "🎙️ 英文教练 (Coaching)":
    st.header("🎙️ 英文教练频道")
    st.write("提升您在国际董事会上的沟通魅力。")
    
    if articles:
        all_vocab = {}
        for a in articles: all_vocab.update(a.get('vocabulary', {}))
        
        st.subheader("🔥 今日高阶词汇")
        cols = st.columns(3)
        for i, (word, mean) in enumerate(all_vocab.items()):
            cols[i%3].metric(label=mean, value=word)
    
    st.divider()
    st.markdown("#### 💬 实战场景")
    st.code("Topic: Strategy Pivot\n'We need to leverage our core competencies to explore the second curve.'")
