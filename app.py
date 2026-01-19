import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

# 加载数据并增加防御逻辑
def load_data():
    if not os.path.exists("data.json"): return {}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        # 补全缺失键值对
        if "weekly_question" not in d: d["weekly_question"] = {"cn":"思考中", "en":"Thinking"}
        return d

data = load_data()

# AI Coach 对话引擎
def call_coach(user_input, art):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    ctx = f"背景文章: {art['title']}\n案例: {art.get('case_study','')}\n反思: {art.get('reflection_flow',[])}"
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是 Read & Rise AI 教练。当前上下文：\n{ctx}"},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.4
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except: return "⚠️ Coach 连接失败。请确保 DEEPSEEK_API_KEY 已正确配置在环境变量中。"

# 侧边栏导航
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "🚀 全球快报"])

# --- 🏠 Dashboard ---
if menu == "🏠 Dashboard":
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:30px;border-radius:20px;color:white;border-left:10px solid #38BDF8;">
        <h4 style="color:#38BDF8;margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size:1.5rem;font-weight:bold;margin-top:10px;">“{data['weekly_question'].get('cn')}”</p>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.metric("今日捕获智库情报", f"{len(data.get('briefs',[]))} 篇")

# --- 🚀 全球快报 (左右联动修复版) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    
    with col_l:
        st.header("🚀 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.container(border=True):
                st.subheader(art['title'])
                st.caption(f"源自: {art.get('source')} | 模型: {art.get('related_model')}")
                
                t1, t2, t3 = st.tabs(["深度摘要", "词汇库", "案例 & 反思"])
                with t1:
                    # 修复 TypeError 的核心逻辑
                    st.write("**EN Summary:**")
                    en_s = art.get('en_summary', [])
                    if isinstance(en_s, list): 
                        for s in en_s: st.write(f"• {s}")
                    else: st.write(en_s)
                    
                    st.write("**中文摘要:**")
                    cn_s = art.get('cn_summary', [])
                    if isinstance(cn_s, list):
                        for s in cn_s: st.write(f"• {s}")
                    else: st.write(cn_s)
                with t2:
                    for v in art.get('vocab_bank', []):
                        st.write(f"🔹 **{v['word']}**: {v['meaning']}")
                with t3:
                    st.info(f"🔍 案例: {art.get('case_study')}")
                    for q in art.get('reflection_flow', []): st.warning(q)
                
                if st.button("🎙️ 开启针对性对话", key=f"chat_btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.history = []

    with col_r:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            active = st.session_state.active_art
            st.info(f"正在对话：《{active['title']}》")
            
            chat_box = st.container(height=500)
            if "history" not in st.session_state: st.session_state.history = []
            
            for m in st.session_state.history:
                with chat_box.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("向教练提问..."):
                st.session_state.history.append({"role": "user", "content": p})
                with chat_box.chat_message("user"): st.markdown(p)
                with chat_box.chat_message("assistant"):
                    r = call_coach(p, active)
                    st.markdown(r)
                    st.session_state.history.append({"role": "assistant", "content": r})
        else:
            st.info("请在左侧点击按钮，开启文章关联对话。")
