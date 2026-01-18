import streamlit as st
import pandas as pd
import json
import os

# 页面配置与 CSS (保持之前的极简风格)
st.set_page_config(page_title="Read & Rise", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .welcome-text { font-size: 4rem; font-weight: 900; color: #0F172A; }
    .book-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .vocab-card { background: #ffffff; border-left: 5px solid #10416F; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 数据加载
def load_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"articles": [], "books": []}
    return {"articles": [], "books": []}

data = load_data()

# 侧边栏导航
with st.sidebar:
    st.markdown("🏹 Read & Rise")
    menu = st.radio("Navigation", ["🏠 主页", "🚀 今日内参", "📚 精读笔记", "🧠 思维模型", "🎙️ 英文教练"])

# --- 频道 2: 精读笔记 (动态读取 AI 生成的内容) ---
if menu == "📚 精读笔记":
    st.header("📚 精英精读笔记 (AI-Powered)")
    if not data["books"]:
        st.info("书籍笔记同步中...")
    else:
        for book in data["books"]:
            with st.expander(f"📖 {book['book_title']}"):
                st.subheader("核心逻辑 (First Principle)")
                st.write(book['first_principle'])
                st.subheader("战略洞察")
                for insight in book['insights']:
                    st.markdown(f"- {insight}")
                st.success(f"🎙️ **Executive Phrasing:** {book['executive_phrasing']}")

# --- 频道 3: 思维模型 (内置 10 个核心模型) ---
elif menu == "🧠 思维模型":
    st.header("🧠 商业思维模型库 (Top 10)")
    models = {
        "1. 第一性原理 (First Principles)": "回归物理事实，重构解决方案。",
        "2. 第二曲线 (The Second Curve)": "跨越非连续性增长的关键。",
        "3. 复利效应 (Compounding)": "长期价值的指数增长。",
        "4. 边际安全 (Margin of Safety)": "决策中的风险缓冲储备。",
        "5. 帕累托法则 (80/20 Rule)": "聚焦核心，实现产出最大化。",
        "6. 机会成本 (Opportunity Cost)": "评估选择背后放弃的代价。",
        "7. 冗余思维 (Redundancy)": "增强系统的反脆弱性。",
        "8. 胜任力圈 (Circle of Competence)": "在最擅长的领域深耕。",
        "9. 飞轮效应 (Flywheel Effect)": "建立自我驱动的增长闭环。",
        "10. 均值回归 (Regression to the Mean)": "理解周期，保持理性预期。"
    }
    col1, col2 = st.columns(2)
    for i, (m_name, m_desc) in enumerate(models.items()):
        target = col1 if i % 2 == 0 else col2
        with target.expander(m_name):
            st.write(m_desc)
            if "第二曲线" in m_name:
                
            if "飞轮效应" in m_name:
                

# (其他频道代码：主页、内参、教练 保持之前的逻辑即可)
