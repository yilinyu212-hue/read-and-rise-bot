import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# UI 样式
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .header-section { background: #0F172A; padding: 40px; text-align: center; color: white; border-radius: 0 0 30px 30px; }
    .nav-bar { display: flex; justify-content: center; gap: 10px; margin-top: -25px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="header-section"><h1>Read & Rise</h1><p>Read to Rise, Rise to Lead.</p></div>""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "Dashboard"

c1, c2, c3 = st.columns(3)
if c1.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("🚀 Intelligence", use_container_width=True): st.session_state.page = "Intelligence"
if c3.button("🧠 Coach", use_container_width=True): st.session_state.page = "Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res.get("items", []) if isinstance(res, dict) else []
            except: return []
    return []

items = load_data()

if st.session_state.page == "Dashboard":
    st.subheader("Today's Strategic Briefing")
    if items:
        st.info(f"今日必读：{items[0].get('cn_title')}")
    else:
        st.warning("内容同步中，请运行抓取程序或检查 GitHub Actions。")

elif st.session_state.page == "Intelligence":
    for item in items:
        with st.expander(f"📍 {item.get('cn_title')}", expanded=True):
            if os.path.exists(item.get('audio_file','')): st.audio(item['audio_file'])
            t1, t2, t3 = st.tabs(["💡 教练解析", "🔤 英语表达", "🧠 对话 Coach"])
            with t1:
                st.write(item.get("cn_analysis"))
                st.success(f"案例：{item.get('case_study')}")
            with t2:
                for v in item.get('vocab_cards', []):
                    st.write(f"🔹 **{v['word']}**: {v['meaning']}")
            with t3:
                if st.button("就此议题发起咨询", key=item.get('cn_title')):
                    st.session_state.page = "Coach"
                    st.rerun()

elif st.session_state.page == "Coach":
    st.header("🧠 AI Executive Coach")
    st.chat_input("描述您的管理挑战...")
