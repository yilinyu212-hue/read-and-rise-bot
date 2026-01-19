import streamlit as st
import json, os, requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Read & Rise | Executive Decision", layout="wide", page_icon="🏹")

# --- 核心：Coach 唤醒函数 ---
def call_coach(user_input, art):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key: return "❌ Coach 离线：请在服务器配置 DEEPSEEK_API_KEY。"
    
    # 读取智库资产增加对话深度
    assets = ""
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            assets = str(json.load(f).get("books", []))

    try:
        res = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是 Read&Rise AI 教练。背景文：{art['title']}。用户智库：{assets}。请用合伙人的口吻提供决策建议。"},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.5
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except: return "⚠️ 教练忙碌中，请稍后。"

# --- 数据加载 ---
def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[]}
    with open("data.json", "r", encoding="utf-8") as f: return json.load(f)

data = load_data()

# --- UI 渲染 ---
st.sidebar.title("🏹 READ & RISE")
menu = st.sidebar.radio("决策中心", ["🏠 Dashboard", "🚀 全球快报", "📚 资产智库", "⚙️ 资产入库"])

if menu == "🏠 Dashboard":
    st.markdown("### Hi, Leaders! 👋")
    st.write(f"今天是 {datetime.now().strftime('%Y年%m月%d日')}。这是今日为您准备的全球商业内参。")

    # 🎙️ 语音播报区
    st.markdown("""<div style="background:#0F172A; padding:20px; border-radius:15px; color:white; border-left:8px solid #38BDF8;">
        <p style="color:#38BDF8; font-size:0.8rem; font-weight:bold; margin:0;">DAILY AUDIO BRIEFING</p>
        <h3 style="margin:5px 0;">每日商业简报 (BBC Style)</h3>
        </div>""", unsafe_allow_html=True)
    
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
    else:
        st.info("🕒 音频播报正在生成中...")

    st.divider()
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.subheader("🧩 今日决策维度")
        if data.get("briefs"):
            scores = data["briefs"][0].get("model_scores", {})
            fig = go.Figure(data=go.Scatterpolar(r=list(scores.values())+[list(scores.values())[0]], theta=list(scores.keys())+[list(scores.keys())[0]], fill='toself'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("📊 智库状态")
        st.metric("入库资产", len(data.get("books", [])))
        st.metric("今日内参", len(data.get("briefs", [])))

elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.55, 0.45])
    with col_l:
        st.header("🌍 全球内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📍 {art['source']} | {art['title']}", expanded=(i==0)):
                t1, t2, t3 = st.tabs(["💡 摘要与案例", "🧠 反思提问", "📖 商业词汇"])
                with t1:
                    for s in art.get('cn_summary', []): st.write(f"• {s}")
                    st.info(f"**实战案例：**\n{art.get('case_study')}")
                with t2:
                    for q in art.get('reflection_flow', []): st.write(f"❓ {q}")
                with t3:
                    for v in art.get('vocab_bank', []): st.write(f"**{v['word']}**: {v['meaning']}")
                
                if st.button("🎙️ 呼叫 Coach 对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.chat_history = []
    with col_r:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            container = st.container(height=500, border=True)
            for m in st.session_state.get('chat_history', []):
                with container.chat_message(m["role"]): st.write(m["content"])
            
            if p := st.chat_input("询问 Coach 实战建议..."):
                st.session_state.chat_history.append({"role": "user", "content": p})
                with container.chat_message("user"): st.write(p)
                with container.chat_message("assistant"):
                    r = call_coach(p, st.session_state.active_art)
                    st.write(r)
                    st.session_state.chat_history.append({"role": "assistant", "content": r})
        else:
            st.info("请从左侧选择文章开启对话。")

elif menu == "⚙️ 资产入库":
    st.header("⚙️ 资产录入")
    with st.form("add_asset"):
        t = st.text_input("书名/模型名称")
        c = st.text_input("核心逻辑")
        i = st.text_area("深度洞察")
        if st.form_submit_button("入库"):
            data["books"].append({"title":t, "concept":c, "insight":i})
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.success("入库成功！")
