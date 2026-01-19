import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- 1. 商务视觉与横向导航 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .header-section { background: #0F172A; padding: 40px; text-align: center; color: white; border-radius: 0 0 30px 30px; }
    .slogan { font-size: 1.2rem; opacity: 0.8; font-style: italic; margin-top: 10px; }
    .nav-bar { display: flex; justify-content: center; gap: 10px; margin-top: -25px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="header-section"><h1>Read & Rise</h1><div class="slogan">Read to Rise, Rise to Lead.</div></div>""", unsafe_allow_html=True)

# 状态初始化
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "messages" not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Welcome, Leader. I am your Executive Coach. How shall we Rise today?"}]

# 横向导航
c1, c2, c3 = st.columns(3)
if c1.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("🚀 Intelligence", use_container_width=True): st.session_state.page = "Intelligence"
if c3.button("🧠 Coach", use_container_width=True): st.session_state.page = "Coach"

# 数据加载
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res.get("items", []) if isinstance(res, dict) else []
            except: return []
    return []

items = load_data()

# --- 2. 页面分发 ---

if st.session_state.page == "Dashboard":
    st.subheader("Today's Executive Briefing")
    if items:
        top = items[0]
        st.info(f"**今日核心决策建议：** {top.get('cn_title')}")
        st.write(top.get('cn_analysis'))
    else:
        st.warning("智库内容同步中...")

elif st.session_state.page == "Intelligence":
    for item in items:
        with st.expander(f"📍 {item.get('cn_title')}", expanded=True):
            if os.path.exists(item.get('audio_file','')): st.audio(item['audio_file'])
            t1, t2, t3 = st.tabs(["💡 教练解析", "🔤 英语表达", "🧠 深度对话"])
            with t1:
                st.write(item.get("cn_analysis"))
                st.success(f"**Management Case:** {item.get('case_study')}")
            with t2:
                for v in item.get('vocab_cards', []):
                    st.write(f"🔹 **{v['word']}**: {v['meaning']}")
            with t3:
                st.write("**带着思考去 Rise:**")
                for q in item.get('reflection_flow', []): st.warning(q)
                if st.button("就此议题咨询 AI 教练", key=f"btn_{item.get('cn_title')}"):
                    # 联动逻辑：把问题塞进 Session，跳转页面
                    st.session_state.messages.append({"role": "user", "content": f"我想聊聊关于《{item.get('cn_title')}》的管理挑战。"})
                    st.session_state.page = "Coach"
                    st.rerun()

elif st.session_state.page == "Coach":
    st.header("🧠 AI Executive Coach")
    st.caption("Read to Rise, Rise to Lead.")

    # 渲染历史消息
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # 聊天输入框 (关键修复：确保它在最外层，不被任何 if 嵌套)
    if prompt := st.chat_input("Describe your management challenge or language query..."):
        # 1. 显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 2. 生成教练回复 (此处可对接 API，目前为专业占位回复)
        with st.chat_message("assistant"):
            response = "As your coach, I see a key opportunity here. Let's analyze this from the perspective of your leadership growth..."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
