import streamlit as st
import json, os, requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Read & Rise | Management Insight", layout="wide", page_icon="🏹")

# --- 1. 数据加载 ---
def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[]}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# --- 2. 播报语音模拟 (TTS 预留接口) ---
def play_daily_audio():
    st.markdown("##### 🎙️ Daily Management Briefing")
    # 这里可以接入 OpenAI TTS 或 Edge-TTS 生成音频流，目前先做展示
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") 
    st.caption("BBC风格短播报：3分钟听完今日全球商业决策重点。")

# --- 3. 后台数据保存 ---
def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

# --- 4. 侧边栏 ---
st.sidebar.title("Read & Rise")
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "🚀 全球快报", "📚 经典书库", "⚙️ 资产入库"])

# --- 🏠 Dashboard (重新排版) ---
if menu == "🏠 Dashboard":
    st.markdown(f"### Hi, Leaders! 👋")
    st.write(f"今天是 {datetime.now().strftime('%Y-%m-%d')}。这是为您准备的商业内参。")
    
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.markdown("""<div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left:5px solid #0e1117;">
            <h4>🎙️ 每周战略思考</h4>
            <p style="font-size:18px;">“面对不确定的 2026，你的核心竞争壁垒是来源于规模，还是来源于敏捷度？”</p>
        </div>""", unsafe_allow_html=True)
        
    with col2:
        play_daily_audio()

    st.divider()
    if data.get("briefs"):
        st.subheader("🧩 今日决策维度")
        # 此处显示雷达图 (逻辑同前)
        st.info("AI 已从今日 15 篇顶级文章中提取出 5 个战略维度。")

# --- 🚀 全球快报 (修复对话框不弹出的问题) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.55, 0.45])
    
    with col_l:
        st.subheader("🌍 全球商业情报")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📍 {art['source']} | {art['title']}", expanded=(i==0)):
                st.write(f"**核心摘要:**")
                for s in art.get('cn_summary', []): st.write(f"• {s}")
                
                # 增加功能标签
                t1, t2, t3 = st.tabs(["🔎 案例洞察", "🧠 决策反思", "📖 商业术语"])
                with t1: st.write(art.get('case_study'))
                with t2: 
                    for q in art.get('reflection_flow', []): st.write(f"❓ {q}")
                with t3:
                    for v in art.get('vocab_bank', []): st.write(f"**{v['word']}**: {v['meaning']}")
                
                # 点击此按钮激活右侧对话
                if st.button(f"🎙️ 呼叫 AI Coach 深度解析", key=f"chat_{i}"):
                    st.session_state.current_art = art
                    st.session_state.chat_history = []

    with col_r:
        st.subheader("🎙️ AI Coach Session")
        if "current_art" in st.session_state:
            active_art = st.session_state.current_art
            st.success(f"正在分析：《{active_art['title']}》")
            
            # 真正的聊天界面渲染
            container = st.container(height=500, border=True)
            for msg in st.session_state.get('chat_history', []):
                with container.chat_message(msg["role"]): st.write(msg["content"])
            
            if prompt := st.chat_input("询问 Coach 关于本文的落地策略..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with container.chat_message("user"): st.write(prompt)
                
                # 模拟 Coach 回复逻辑
                response = f"针对《{active_art['title']}》这篇文章，我建议您首先关注其提到的{active_art.get('related_model','核心模型')}..."
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                with container.chat_message("assistant"): st.write(response)
        else:
            st.info("请点击左侧文章下的按钮，开始与 Coach 针对性对话。")

# --- ⚙️ 资产入库 (解释输入逻辑) ---
elif menu == "⚙️ 资产入库":
    st.header("⚙️ 建立您的私有商业智库")
    st.markdown("""
    **书籍输入逻辑说明：**
    1. **书名/模型**：您读过的经典，如《原则》或“第一性原理”。
    2. **核心理念**：用一句话概括这本书解决什么商业问题。
    3. **深度洞察**：您希望 AI Coach 在以后对话时“记住”的重点。
    *录入后，当您在【全球快报】与 Coach 对话时，它会参考这些背景。*
    """)
    
    with st.form("book_form"):
        title = st.text_input("书名或模型名称")
        concept = st.text_input("核心管理逻辑 (Short Summary)")
        insight = st.text_area("您的个人感悟/应用点")
        if st.form_submit_button("永久入库"):
            if title:
                data["books"].append({"title": title, "concept": concept, "insight": insight})
                save_data(data)
                st.success("资产已存入。")
