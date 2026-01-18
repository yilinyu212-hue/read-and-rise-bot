import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. 页面配置与主题
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide", page_icon="🏹")

# 2. 高级 CSS 样式注入 (提升 UI 质感)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stApp { color: #1a1a1a; }
    .leader-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border-top: 5px solid #10416F;
        margin-bottom: 25px;
    }
    .en-term {
        color: #10416F;
        font-weight: bold;
        background: #eef2f6;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 10px;
        background: #10416F;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 侧边栏导航 ---
with st.sidebar:
    st.markdown("# 🏹 Read & Rise")
    st.markdown("### AI Business Coach")
    st.divider()
    menu = st.radio("Focus Area", ["🚀 Today's Briefing", "🧠 Model Library", "🎙️ Executive English", "📈 Strategy Map"])
    st.divider()
    st.markdown("#### 💡 Today's Focus")
    st.success("Focus: Resilience & Innovation")

# --- 数据加载 ---
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

articles = load_data()

# ================= 频道 1: 今日内参 (Executive Briefing) =================
if menu == "🚀 Today's Briefing":
    st.markdown('<p style="font-size:3rem; font-weight:800; color:#10416F; margin-bottom:0;">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.write(f"📅 Sync Date: {datetime.now().strftime('%Y-%m-%d')} | Global Insight Feed")
    
    # 增加搜索与过滤
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Search Insights", placeholder="e.g., Digital Transformation, ESG, AI...")
    
    st.divider()

    if not articles:
        st.warning("Coach is analyzing today's news... Please check back in 5 mins.")
    else:
        for art in articles:
            if search.lower() in art['title'].lower() or search.lower() in art.get('cn_analysis', '').lower():
                with st.container():
                    st.markdown(f'''
                    <div class="leader-card">
                        <span class="badge">{art['source']}</span>
                        <h2 style="margin-top:10px;">{art['title']}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    tab1, tab2, tab3 = st.tabs(["🇨🇳 战略拆解 (Coach Insight)", "🇬🇧 CEO Summary", "💬 实战金句 (Phrasing)"])
                    
                    with tab1:
                        st.markdown(art.get('cn_analysis', 'Analysis pending...'))
                        
                    with tab2:
                        st.info(f"**Core Logic:**\n\n{art.get('en_summary', 'Pending...')}")
                        
                    with tab3:
                        st.markdown("#### 如何在会议中引用此洞察：")
                        vocab = art.get('vocabulary', {"Pivotal": "关键的"})
                        for term, mean in vocab.items():
                            st.markdown(f"- \"Based on the latest data, we need to make a **{term}** ({mean}) shift in our strategy.\"")

# ================= 频道 2: 思维模型 (Model Library) =================
elif menu == "🧠 Model Library":
    st.header("🧠 商业思维模型库 (Mental Models)")
    st.write("掌握全球通用决策逻辑。")
    
    # 使用卡片布局增加“厚度”
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        with st.expander("The Second Curve | 第二曲线", expanded=True):
            st.markdown("""
            **核心逻辑**：在第一曲线到达巅峰前，启动第二增长曲线。
            **CEO 话术**： "We must identify our next S-curve while our core business is still thriving."
            """)
    with col_m2:
        with st.expander("First Principles | 第一性原理", expanded=True):
            st.markdown("""
            **核心逻辑**：拆解复杂问题至基本事实，重新构建。
            **CEO 话术**： "Let's boil this down to the first principles and re-evaluate our assumptions."
            """)

# ================= 频道 3: 执行英文 (Executive English) =================
elif menu == "🎙️ Executive English":
    st.header("🎙️ 领导者表达教练 (Executive Phrasing)")
    st.write("将商业洞察转化为领导力语言。")
    
    if articles:
        st.subheader("🔥 今日核心术语 (Key Business Vocabulary)")
        for art in articles:
            for term, mean in art.get('vocabulary', {}).items():
                st.markdown(f"- <span class='en_term'>{term}</span> : {mean}", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### 🚀 会议开场白模板 (Meeting Starters)")
        st.code("Good morning team, based on today's HBR analysis, I'd like to pivot our discussion towards...", language='text')

# ================= 频道 4: 战略地图 (Strategy Map) =================
elif menu == "📈 Strategy Map":
    st.header("📈 战略能力仪表盘")
    if articles:
        # 汇总展示今日资讯的能量分布
        avg_scores = {
            '战略思维': sum(a['scores']['战略思维'] for a in articles) / len(articles),
            '组织进化': sum(a['scores']['组织进化'] for a in articles) / len(articles),
            '决策韧性': sum(a['scores']['决策韧性'] for a in articles) / len(articles),
            '行业洞察': sum(a['scores']['行业洞察'] for a in articles) / len(articles),
            '技术视野': sum(a['scores']['技术视野'] for a in articles) / len(articles),
        }
        df = pd.DataFrame(list(avg_scores.items()), columns=['Dimension', 'Strength'])
        st.bar_chart(df.set_index('Dimension'))
        st.success("今日建议：重点强化您的 **技术视野**，相关文章已在内参中置顶。")
