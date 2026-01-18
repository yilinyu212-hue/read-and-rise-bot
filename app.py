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

# ================= 2. 专业级 CSS 注入 =================
st.markdown("""
    <style>
    /* 全局背景与字体 */
    .main { background-color: #f8f9fa; }
    
    /* 自定义卡片样式 */
    .leader-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 8px solid #10416F;
        margin-bottom: 20px;
    }
    
    /* 英文术语高亮 */
    .en-term {
        color: #10416F;
        font-weight: bold;
        background: #eef2f6;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #d1d9e0;
    }
    
    /* 标题样式 */
    .welcome-text { font-size: 3rem; font-weight: 800; color: #10416F; margin-bottom: 0; }
    
    /* 侧边栏样式优化 */
    .css-1d391kg { background-color: #10416F; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. 数据加载逻辑 =================
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Data sync error: {e}")
            return []
    return []

articles = load_data()

# ================= 4. 侧边栏导航 =================
with st.sidebar:
    st.markdown("<h1 style='color: white;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a0aec0;'>AI Business Coach & English Mentor</p>", unsafe_allow_html=True)
    st.divider()
    
    # 频道切换
    menu = st.radio(
        "选择频道 / Navigate",
        ["🚀 今日内参 Briefing", "🧠 思维模型 Library", "🎙️ 英文教练 Coaching", "📊 能力看板 Metrics"]
    )
    
    st.divider()
    st.info("💡 **Coach Insight**:\n真正的领导力源于在信息过载中保持战略定力。")

# ================= 5. 频道内容实现 =================

# --- 频道 1: 今日内参 ---
if menu == "🚀 今日内参 Briefing":
    st.markdown('<p class="welcome-text">Hi, Leaders!</p>', unsafe_allow_html=True)
    st.write(f"📅 Sync Date: {datetime.now().strftime('%Y-%m-%d')} | 全球商业趋势同步完成")
    
    search = st.text_input("🔍 检索洞察 (Search Insights)", placeholder="输入关键字，如 AI, Leadership, ESG...")
    st.divider()

    if not articles:
        st.warning("内容正在由 AI 教练生成中，请运行爬虫后刷新。")
    else:
        for art in articles:
            # 搜索过滤
            if search.lower() in art.get('title','').lower() or search.lower() in art.get('cn_analysis','').lower():
                st.markdown(f'''
                    <div class="leader-card">
                        <p style="color:#666; font-size:0.8rem; margin-bottom:5px;">{art.get('source')} · {art.get('date')}</p>
                        <h2 style="margin-top:0;">{art.get('title')}</h2>
                    </div>
                ''', unsafe_allow_html=True)
                
                # 双语切换标签
                tab1, tab2, tab3 = st.tabs(["🇨🇳 中文深度拆解", "🇬🇧 English Summary", "💬 CEO Phrasing"])
                
                with tab1:
                    st.markdown(art.get('cn_analysis', '内容同步中...'))
                    st.link_button("🌐 查看原文 Original Link", art.get('link'))
                
                with tab2:
                    st.info(f"**Key Takeaways:**\n\n{art.get('en_summary', 'N/A')}")
                
                with tab3:
                    st.markdown("#### 🚀 场景化表达 (CEO English)")
                    vocab = art.get('vocabulary', {})
                    if vocab:
                        for term, mean in vocab.items():
                            st.write(f"👉 *\"The current market trend is **{term}** ({mean}), which requires us to...\"*")
                    else:
                        st.write("今日暂无词汇推荐。")
                st.markdown("<br>", unsafe_allow_html=True)

# --- 频道 2: 思维模型馆 (包含思维导图) ---
elif menu == "🧠 思维模型 Library":
    st.header("🧠 商业思维模型库 (Mental Models)")
    st.write("视觉化拆解全球顶尖 CEO 的底层思维逻辑。")
    
    model_name = st.selectbox("选择要学习的模型:", ["第二曲线 (The Second Curve)", "第一性原理 (First Principles)"])
    
    col_text, col_graph = st.columns([1, 1.2])
    
    if model_name == "第二曲线 (The Second Curve)":
        with col_text:
            st.markdown("""
            ### 📈 核心逻辑
            1. **第一曲线**：任何企业或业务都有其生命周期，从增长到衰退。
            2. **破局点**：在第一曲线尚未走下坡路之前，投入资源开启新增长。
            3. **第二曲线**：新业务模式替代旧模式，实现跨越式增长。
            
            **CEO 话术**: *"We must disrupt ourselves before others do."*
            """)
        with col_graph:
            # 渲染思维导图
            
            st.graphviz_chart('''
                digraph {
                    node [fontname="SimHei", shape=box, style=filled, fillcolor="#E3F2FD", color="#10416F"]
                    "第二曲线策略" -> "第一曲线 (成熟期)"
                    "第二曲线策略" -> "转换期 (资源重组)"
                    "第二曲线策略" -> "新增长极 (未来价值)"
                    "第一曲线 (成熟期)" -> "保持现金流"
                    "新增长极 (未来价值)" -> "指数增长"
                }
            ''')

    elif model_name == "第一性原理 (First Principles)":
        with col_text:
            st.markdown("""
            ### 🔬 核心逻辑
            1. **拆解假设**：剥离那些“一直以来都是这样”的成见。
            2. **原子事实**：找到事情最基础、最不可再分的物理事实。
            3. **底层重组**：从最底层逻辑出发构建全新的方案（如 SpaceX）。
            
            **CEO 话术**: *"Let's drill down to the fundamental truths here."*
            """)
        with col_graph:
            
            st.graphviz_chart('''
                digraph {
                    node [fontname="SimHei", shape=ellipse, style=filled, fillcolor="#F1F8E9", color="#2E7D32"]
                    "第一性原理" -> "识别旧假设"
                    "第一性原理" -> "拆解至事实"
                    "第一性原理" -> "重新架构方案"
                    "拆解至事实" -> "成本要素"
                    "拆解至事实" -> "物理限制"
                }
            ''')

# --- 频道 3: 英文教练 ---
elif menu == "🎙️ 英文教练 Coaching":
    st.header("🎙️ 领导者表达教练 (Executive Phrasing)")
    st.write("同步今日外刊中的高阶词汇，提升您在国际会议中的表达专业度。")
    
    if articles:
        st.subheader("🔥 今日核心术语 (Key Vocabulary)")
        combined_vocab = {}
        for art in articles:
            combined_vocab.update(art.get('vocabulary', {}))
        
        cols = st.columns(3)
        for i, (word, mean) in enumerate(combined_vocab.items()):
            cols[i % 3].markdown(f"<span class='en-term'>{word}</span><br>{mean}", unsafe_allow_html=True)
            
        st.divider()
        st.markdown("#### 🛠️ 实战话术卡片 (Action Cards)")
        st.info("**如何谈论“转型” (Pivoting)**:\n\"In response to the market volatility, we are executing a strategic pivot to capture high-growth segments.\"")
    else:
        st.warning("暂无数据，请同步爬虫。")

# --- 频道 4: 能力看板 ---
elif menu == "📊 能力看板 Metrics":
    st.header("📊 战略能力仪表盘")
    st.write("基于今日资讯，您的思维维度提升如下：")
    
    if articles:
        # 计算平均分
        scores_df = pd.DataFrame([a['scores'] for a in articles])
        avg_scores = scores_df.mean().reset_index()
        avg_scores.columns = ['Dimension', 'Strength']
        
        st.bar_chart(avg_scores.set_index('Dimension'))
        st.markdown(f"> **教练总结**：今日阅读让您在 **{avg_scores.loc[avg_scores['Strength'].idxmax(), 'Dimension']}** 维度获得了最显著的提升。")
    else:
        st.caption("同步数据后即可查看能力雷达。")
