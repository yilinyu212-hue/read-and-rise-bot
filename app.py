import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= 1. 页面基本配置 =================
st.set_page_config(
    page_title="Read & Rise | AI Business Coach",
    layout="wide",
    page_icon="🏹",
    initial_sidebar_state="expanded"
)

# ================= 2. 深度视觉定制 (CSS) =================
st.markdown("""
    <style>
    /* 全局背景 */
    .stApp { background-color: #f4f7f9; }
    
    /* Hi Leaders 欢迎语 */
    .welcome-text { 
        font-size: 3.5rem; 
        font-weight: 800; 
        color: #10416F; 
        margin-bottom: 0;
        letter-spacing: -1px;
    }
    
    /* 文章卡片 */
    .leader-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-top: 4px solid #10416F;
        height: 100%;
    }
    
    /* 英文词汇高亮 */
    .en-term {
        color: #10416F;
        font-weight: bold;
        background: #eef2f6;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }

    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background-color: #10416F;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ================= 3. 稳健的数据加载逻辑 =================
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            st.error(f"数据解析异常: {e}")
            return []
    return []

articles = load_data()

# ================= 4. 侧边栏导航控制 =================
with st.sidebar:
    st.markdown("<h1 style='color: white;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e0;'>AI Business Coach & English Mentor</p>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.radio(
        "选择频道 / Channels",
        ["🚀 今日内参 Briefing", "🧠 思维模型 Library", "🎙️ 英文教练 Coaching", "📊 战略看板 Metrics"],
        index=0
    )
    
    st.divider()
    st.markdown("#### 💬 Coach Status")
    st.success("Global Feed: Connected")
    st.caption(f"Syncing from 12 top sources...")

# ================= 5. 各频道逻辑实现 =================

# --- 频道 1: 今日内参 ---
if menu == "🚀 今日内参 Briefing":
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.write(f"📅 {datetime.now().strftime('%Y-%m-%d')} | 您有 {len(articles)} 条来自全球顶级智库的新情报")
    
    # 搜索与过滤
    search = st.text_input("🔍 检索洞察 (Search Insights)", placeholder="输入关键字，如 AI, Leadership, ESG...")
    st.divider()

    if not articles:
        st.info("🔄 **正在拉取 12 个全球源...**\n\n数据正在从 HBR, McKinsey, MIT 等源实时同步。请确保 GitHub Actions 运行成功。")
    else:
        # 两列布局展示内参
        for i in range(0, len(articles), 2):
            col_a, col_b = st.columns(2)
            
            # 左列文章
            with col_a:
                art = articles[i]
                if search.lower() in art.get('title','').lower() or search.lower() in art.get('cn_analysis','').lower():
                    with st.container():
                        st.markdown(f'''
                            <div class="leader-card">
                                <p style="color:#0d47a1; font-weight:bold; font-size:0.8rem;">{art.get('source', 'INSIGHT')}</p>
                                <h3 style="margin-top:0;">{art.get('title')}</h3>
                            </div>
                        ''', unsafe_allow_html=True)
                        tab1, tab2 = st.tabs(["🇨🇳 深度拆解", "🇬🇧 Summary"])
                        with tab1:
                            st.markdown(art.get('cn_analysis', '解析中...'))
                            st.link_button("🌐 阅读原文", art.get('link'))
                        with tab2:
                            st.info(art.get('en_summary', 'Summarizing...'))
            
            # 右列文章
            if i + 1 < len(articles):
                with col_b:
                    art = articles[i+1]
                    if search.lower() in art.get('title','').lower() or search.lower() in art.get('cn_analysis','').lower():
                        with st.container():
                            st.markdown(f'''
                                <div class="leader-card">
                                    <p style="color:#0d47a1; font-weight:bold; font-size:0.8rem;">{art.get('source', 'INSIGHT')}</p>
                                    <h3 style="margin-top:0;">{art.get('title')}</h3>
                                </div>
                            ''', unsafe_allow_html=True)
                            tab1, tab2 = st.tabs(["🇨🇳 深度拆解", "🇬🇧 Summary"])
                            with tab1:
                                st.markdown(art.get('cn_analysis', '解析中...'))
                                st.link_button("🌐 阅读原文", art.get('link'))
                            with tab2:
                                st.info(art.get('en_summary', 'Summarizing...'))

# --- 频道 2: 思维模型馆 ---
elif menu == "🧠 思维模型 Library":
    st.header("🧠 商业思维模型库 (Mental Models)")
    st.write("掌握全球顶尖 CEO 的底层决策逻辑。")
    
    # 模拟内置高频模型
    model_choice = st.selectbox("选择模型进行可视化拆解:", ["第二曲线 (The Second Curve)", "第一性原理 (First Principles)"])
    
    col_l, col_r = st.columns([1, 1.2])
    if model_choice == "第二曲线 (The Second Curve)":
        with col_l:
            st.markdown("""
            ### 📈 核心逻辑
            - **破局点**：在现有业务(S1)下行前，寻找创新点。
            - **资源重组**：将核心竞争力迁移至新领域。
            - **指数增长**：跨越非连续性，开启 S2 增长。
            """)
            st.warning("**CEO Phrasing**: 'We must identify our next S-curve to ensure long-term viability.'")
        with col_r:
            st.graphviz_chart('''
                digraph { node[fontname="SimHei",shape=box,color="#10416F"] 
                "第二曲线策略" -> "第一曲线(Cash Flow)"; 
                "第二曲线策略" -> "转换实验(Innovation)"; 
                "第二曲线策略" -> "未来爆发点"; }
            ''')
            

    elif model_choice == "第一性原理 (First Principles)":
        with col_l:
            st.markdown("""
            ### 🔬 核心逻辑
            - **解构成见**：不听“别人是怎么做的”。
            - **原子事实**：找到不可再分的物理基础。
            - **底层重组**：从零构建最有效方案。
            """)
            st.warning("**CEO Phrasing**: 'Let's drill down to the fundamental truths and rebuild from there.'")
        with col_r:
            st.graphviz_chart('''
                digraph { node[fontname="SimHei",shape=ellipse,color="#2E7D32"] 
                "第一性原理" -> "识别旧假设" -> "原子事实" -> "重新构架新系统"; }
            ''')
            

# --- 频道 3: 英文教练 ---
elif menu == "🎙️ 英文教练 Coaching":
    st.header("🎙️ 领导者表达教练 (Executive Phrasing)")
    st.write("同步今日外刊中的高阶词汇，提升您在国际会议中的专业度。")
    
    # 整合所有抓取到的词汇
    if articles:
        all_vocab = {}
        for a in articles: all_vocab.update(a.get('vocabulary', {}))
        
        st.subheader("🔥 今日核心术语库")
        v_cols = st.columns(3)
        for i, (word, mean) in enumerate(all_vocab.items()):
            v_cols[i % 3].markdown(f"<span class='en-term'>{word}</span> : {mean}", unsafe_allow_html=True)
            
        st.divider()
        st.subheader("💬 会议实战模板 (Executive Meeting Templates)")
        st.code("Topic: Introducing a Shift\n'Based on the insights from [Source], I recommend we pivot our focus towards...'")
        st.code("Topic: Analyzing Efficiency\n'We need to address the bottleneck in our current workflow to maintain scalability.'")
    else:
        st.info("今日术语同步中...")

# --- 频道 4: 战略看板 ---
elif menu == "📊 战略看板 Metrics":
    st.header("📊 战略能力仪表盘")
    if articles:
        # 数据可视化
        scores_list = [a['scores'] for a in articles if 'scores' in a]
        if scores_list:
            df = pd.DataFrame(scores_list).mean().reset_index()
            df.columns = ['Dimension', 'Score']
            st.bar_chart(df.set_index('Dimension'))
            st.success("今日建议：您的“战略思维”维度受 HBR 和 Economist 启发最深，建议重点关注。")
    else:
        st.caption("暂无动态评分数据。")
