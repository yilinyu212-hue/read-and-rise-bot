import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

# ================= 1. 安全加载数据 =================
def load_data():
    if not os.path.exists("data.json"): return {}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        # 兜底 Key 缺失
        if "weekly_question" not in d:
            d["weekly_question"] = {"cn": "正在思考布局...", "en": "Strategy thinking..."}
        return d

data = load_data()

# ================= 2. 对话关联逻辑 =================
def call_coach(user_input, art_context):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    # 将文章的核心要点喂给对话模型
    ctx = f"文章: {art_context['title']}\n案例: {art_context.get('case_study','')}\n提问: {art_context.get('reflection_flow',[])}"
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是针对此文的专业私教。背景：\n{ctx}"},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.5
            })
        return res.json()['choices'][0]['message']['content']
    except: return "Coach 连接失败，请检查 API 配置。"

# ================= 3. 页面布局 =================
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "🚀 全球快报"])

if menu == "🏠 Dashboard":
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:30px;border-radius:20px;color:white;border-left:10px solid #38BDF8;">
        <h4 style="color:#38BDF8;margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size:1.5rem;font-weight:bold;margin-top:10px;">“{data['weekly_question']['cn']}”</p>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.metric("今日捕获", f"{len(data.get('briefs', []))} 篇智库情报")

elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        st.header("🚀 全球智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.container(border=True):
                st.subheader(art['title'])
                t1, t2, t3 = st.tabs(["深度摘要", "管理词汇", "案例反思"])
                with t1:
                    # 解决列表拼接报错的核心逻辑
                    for lang, key in [("EN Summary", "en_summary"), ("中文摘要", "cn_summary")]:
                        st.write(f"**{lang}:**")
                        items = art.get(key, [])
                        if isinstance(items, list):
                            for item in items: st.write(f"• {item}")
                        else: st.write(items)
                with t2:
                    for v in art.get('vocab_bank', []):
                        st.write(f"🔹 **{v['word']}**: {v['meaning']}")
                with t3:
                    st.info(f"🔍 案例解析: {art.get('case_study')}")
                    for q in art.get('reflection_flow', []): st.warning(q)
                
                if st.button("🎙️ 针对此文开启对话", key=f"btn_{i}"):
                    st.session_state.current_art = art
                    st.session_state.history = []

    with col_r:
        st.header("🎙️ Coach Session")
        if "current_art" in st.session_state:
            curr = st.session_state.current_art
            st.info(f"正在深度研读：{curr['title']}")
            chat_box = st.container(height=500)
            if "history" not in st.session_state: st.session_state.history = []
            for m in st.session_state.history:
                with chat_box.chat_message(m["role"]): st.write(m["content"])
            
            if p := st.chat_input("向教练提问..."):
                st.session_state.history.append({"role": "user", "content": p})
                with chat_box.chat_message("user"): st.write(p)
                with chat_box.chat_message("assistant"):
                    resp = call_coach(p, curr)
                    st.write(resp)
                    st.session_state.history.append({"role": "assistant", "content": resp})
        else:
            st.info("请在左侧点击【开启对话】按钮启动私教 Session。")
