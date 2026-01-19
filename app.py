import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 1. 商务横向导航 UI
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC; }
    .header-section {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 60px 20px; text-align: center; color: white; border-radius: 0 0 40px 40px;
    }
    .slogan { font-size: 1.4rem; opacity: 0.9; font-style: italic; margin-top: 15px; font-family: 'Georgia', serif; }
    .nav-bar { display: flex; justify-content: center; gap: 15px; margin: -25px 0 30px 0; }
    .nav-btn { background: white; border: 1px solid #E2E8F0; padding: 12px 30px; border-radius: 50px; cursor: pointer; font-weight: 600; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# Slogan 展示区
st.markdown("""
<div class="header-section">
    <h1 style='font-size: 3rem; margin: 0;'>Read & Rise</h1>
    <div class="slogan">Read to Rise, Rise to Lead.</div>
</div>
""", unsafe_allow_html=True)

# 横向导航逻辑
if "page" not in st.session_state: st.session_state.page = "Dashboard"

# 使用列模拟导航按钮
n1, n2, n3 = st.columns([1, 1, 1])
with n1: 
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
with n2: 
    if st.button("🚀 Intelligence", use_container_width=True): st.session_state.page = "Intelligence"
with n3: 
    if st.button("🧠 Coach", use_container_width=True): st.session_state.page = "Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"items": []}

data = load_data()
items = data.get("items", [])

# --- 逻辑分发 ---
if st.session_state.page == "Dashboard":
    st.subheader("Executive Insight of the Day")
    if items:
        top = items[0]
        st.info(f"**{top.get('cn_title')}**\n\n{top.get('cn_analysis')}")
        st.markdown(f"**今日思维模型：** `{top.get('mental_model')}`")

elif st.session_state.page == "Intelligence":
    for item in items:
        with st.expander(f"📍 {item.get('cn_title')}", expanded=True):
            if os.path.exists(item.get('audio_file','')): st.audio(item['audio_file'])
            
            t1, t2, t3 = st.tabs(["💡 教练解析", "🔤 英语表达", "🧠 深度反思"])
            with t1:
                st.write(item.get('cn_analysis'))
                st.success(f"**Case Study:**\n{item.get('case_study')}")
            with t2:
                for v in item.get('vocab_cards', []):
                    st.write(f"🔹 **{v['word']}**: {v['meaning']}")
            with t3:
                for r in item.get('reflection_flow', []):
                    st.warning(r)
                if st.button("针对此文发起咨询", key=item.get('cn_title')):
                    st.session_state.pending_q = f"基于文章《{item.get('cn_title')}》，我想讨论：项目在实际管理中的落地..."
                    st.session_state.page = "Coach"
                    st.rerun()

elif st.session_state.page == "Coach":
    st.header("🧠 AI Executive Coach")
    st.caption("Read to Rise, Rise to Lead.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "您好。我是您的 AI 教练。通过刚才的阅读，您产生了什么新的领导力思考？"}]

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 自动带入来自 Intelligence 频道的问题
    default_input = st.session_state.get("pending_q", "")
    
    if prompt := st.chat_input("在这里输入您的困惑..."):
        full_p = f"{default_input} {prompt}" if default_input else prompt
        st.session_state.messages.append({"role": "user", "content": full_p})
        with st.chat_message("user"): st.markdown(full_p)
        
        # 清除待处理问题
        if "pending_q" in st.session_state: del st.session_state.pending_q
        
        with st.chat_message("assistant"):
            response = "作为企业教练，我建议从这个角度思考..." # 这里后续可对接 API
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
