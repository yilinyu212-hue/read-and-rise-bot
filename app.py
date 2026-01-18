import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Read & Rise", layout="wide")

# 清爽样式注入
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .vocab-card { background: white; border-left: 5px solid #10416F; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .book-card { background: white; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

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
    st.title("🏹 Read & Rise")
    menu = st.radio("频道", ["🏠 主页", "🚀 今日内参", "📚 精读笔记", "🧠 思维模型", "🎙️ 英文教练"])

# --- 频道 2: 精读笔记 ---
if menu == "📚 精读笔记":
    st.header("📚 AI 领读：精英精读笔记")
    if not data.get("books"):
        st.info("AI 正在为您解析书籍核心洞察...")
    else:
        for book in data["books"]:
            with st.expander(f"📖 {book['book_title']}", expanded=True):
                st.subheader("第一性原理 (First Principle)")
                st.write(book['first_principle'])
                st.subheader("战略洞察 (Executive Insights)")
                for insight in book['insights']:
                    st.markdown(f"- {insight}")
                st.success(f"🎙️ **高管表达话术:** {book['executive_phrasing']}")

# --- 频道 3: 思维模型 (预置 10 个) ---
elif menu == "🧠 思维模型":
    st.header("🧠 商业思维模型库 (Top 10)")
    models = {
        "1. 第一性原理": "拆解事物至物理本质，重新构建。",
        "2. 第二曲线": "在现有业务达到顶峰前开启新增长点。",
        "3. 飞轮效应": "建立良性循环，让业务自动加速。",
        "4. 边际安全": "为决策预留容错空间，防止系统崩盘。",
        "5. 帕累托法则": "聚焦决定 80% 产出的 20% 核心投入。",
        "6. 复利效应": "通过微小且持续的迭代实现指数级增长。",
        "7. 机会成本": "衡量放弃最高价值替代方案的代价。",
        "8. 反脆弱": "从压力、波动和随机性中获益。",
        "9. 胜任力圈": "专注于自己真正理解并擅长的领域。",
        "10. 沉没成本误区": "理性决策应关注未来，而非已无法收回的成本。"
    }
    col1, col2 = st.columns(2)
    for i, (m_name, m_desc) in enumerate(models.items()):
        target = col1 if i % 2 == 0 else col2
        with target.expander(m_name):
            st.write(m_desc)
            # 修复之前的缩进错误：确保 if 块内有内容
            if "飞轮效应" in m_name:
                st.write("📈 *应用建议：寻找企业中能够互相推动的闭环因素。*")
                
# --- 频道 4: 英文教练 (彻底修复拥挤) ---
elif menu == "🎙️ 英文教练":
    st.header("🎙️ 英文教练：高阶表达卡片")
    if data.get("articles"):
        all_vocab = {}
        for a in data["articles"]: all_vocab.update(a.get('vocabulary', {}))
        
        # 强制两列垂直排列，解决截图 2 的拥挤感
        v_col1, v_col2 = st.columns(2)
        for i, (word, mean) in enumerate(all_vocab.items()):
            target = v_col1 if i % 2 == 0 else v_col2
            target.markdown(f'<div class="vocab-card"><strong>{word}</strong><br><small>{mean}</small></div>', unsafe_allow_html=True)
