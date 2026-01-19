import streamlit as st
import json, os, requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Read & Rise | Executive Insight", layout="wide", page_icon="🏹")

# --- 1. 数据处理 ---
def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[]}
    with open("data.json", "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- 2. 雷达图组件 ---
def draw_radar(scores):
    if not scores: scores = {"战略":50,"创新":50,"洞察":50,"组织":50,"执行":50}
    fig = go.Figure(data=go.Scatterpolar(r=list(scores.values()) + [list(scores.values())[0]],
                                       theta=list(scores.keys()) + [list(scores.keys())[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350, margin=dict(l=40, r=40, t=40, b=40))
    return fig

# --- 3. 导航 ---
menu = st.sidebar.radio("READ & RISE", ["🏠 Dashboard", "🚀 全球快报", "📚 资产智库", "⚙️ 资产入库"])

# --- 🏠 Dashboard ---
if menu == "🏠 Dashboard":
    st.markdown(f"### Hi, Leaders! 👋")
    st.write(f"今天是 {datetime.now().strftime('%Y年%m月%d日')}。这是今日为您生成的全球管理策略内参。")
    
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.markdown(f"""<div style="background-color:#0F172A; padding:25px; border-radius:15px; color:white; border-left:8px solid #38BDF8;">
            <p style="color:#38BDF8; font-weight:bold; margin-bottom:5px;">🎙️ WEEKLY STRATEGY / 每周战略反思</p>
            <h3 style="margin:0;">“面对 2026 的不确定性，你的增长是依赖于红利，还是依赖于核心系统能力的迭代？”</h3>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎙️ Daily Briefing")
        st.caption("3分钟 BBC 风格短平快语音播报（今日重点资讯概览）")
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # 预留 TTS 接口

# --- 🚀 全球快报 (左读右聊) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.55, 0.45])
    with col_l:
        st.header("🌍 Global Insight")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📍 {art['source']} | {art['title']}", expanded=(i==0)):
                t1, t2, t3, t4 = st.tabs(["💡 摘要", "🔎 案例解析", "🧠 深度反思", "📖 商业词汇"])
                with t1:
                    for s in art.get('cn_summary', []): st.write(f"• {s}")
                with t2: st.write(art.get('case_study', '正在生成实战案例...'))
                with t3:
                    for q in art.get('reflection_flow', []): st.write(f"❓ {q}")
                with t4:
                    for v in art.get('vocab_bank', []): st.write(f"**{v['word']}**: {v['meaning']}  \n*{v['example']}*")
                
                if st.button("🎙️ 呼叫 AI Coach 对话", key=f"chat_{i}"):
                    st.session_state.current_art = art
                    st.session_state.chat_history = []

    with col_r:
        st.header("🎙️ Coach Session")
        if "current_art" in st.session_state:
            active_art = st.session_state.current_art
            st.info(f"正在对话：《{active_art['title']}》")
            
            # 对话框渲染
            chat_container = st.container(height=500, border=True)
            if "chat_history" not in st.session_state: st.session_state.chat_history = []
            
            for msg in st.session_state.chat_history:
                with chat_container.chat_message(msg["role"]): st.write(msg["content"])
            
            if prompt := st.chat_input("询问 Coach 关于本文的实战建议..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with chat_container.chat_message("user"): st.write(prompt)
                
                # AI 回复逻辑 (对接 DeepSeek)
                with chat_container.chat_message("assistant"):
                    response = f"基于本文提到的{active_art.get('source')}视角，针对您的提问，我建议重点考察..."
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            st.info("请在左侧选择一篇文章并点击【呼叫 AI Coach 对话】。")

# --- ⚙️ 资产入库 (说明逻辑) ---
elif menu == "⚙️ 资产入库":
    st.header("⚙️ 资产数字化中心")
    st.info("💡 输入逻辑：将您读过的经典书籍或建立的思维模型输入此处。Coach 在以后分析资讯时，会参考这些底层的商业资产。")
    
    with st.form("add_asset"):
        title = st.text_input("书名或思维模型名称 (如:《原则》/ 第一性原理)")
        concept = st.text_input("核心管理逻辑 (一句话总结)")
        insight = st.text_area("个人洞察 (您希望 AI 在对话中运用的知识点)")
        if st.form_submit_button("存入数字资产库"):
            if title:
                data["books"].append({"title": title, "concept": concept, "insight": insight})
                save_data(data)
                st.success(f"资产《{title}》已入库。")
