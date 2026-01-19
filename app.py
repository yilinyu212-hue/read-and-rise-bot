import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- UI 视觉：卡片式设计 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .header-section { background: #0F172A; padding: 40px; text-align: center; color: white; border-radius: 0 0 30px 30px; }
    .slogan { font-size: 1.2rem; opacity: 0.8; font-style: italic; margin-top: 10px; }
    .note-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #E5E7EB; margin-bottom: 20px; }
    .read-tag { color: #2563EB; font-weight: bold; font-size: 1.3rem; }
    .rise-tag { color: #059669; font-weight: bold; font-size: 1.3rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="header-section"><h1>Read & Rise</h1><div class="slogan">Read to Rise, Rise to Lead.</div></div>""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "messages" not in st.session_state: st.session_state.messages = []

# 横向导航
c1, c2, c3 = st.columns(3)
if c1.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("🚀 Intelligence", use_container_width=True): st.session_state.page = "Intelligence"
if c3.button("🧠 Coach", use_container_width=True): st.session_state.page = "Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try: return json.load(f).get("items", [])
            except: return []
    return []

items = load_data()

# --- 逻辑分发 ---
if st.session_state.page == "Dashboard":
    if items:
        st.markdown(f'<div class="note-card"><h2>今日首荐：{items[0].get("cn_title")}</h2><p>{items[0].get("cn_analysis")[:150]}...</p></div>', unsafe_allow_html=True)

elif st.session_state.page == "Intelligence":
    if items:
        titles = [i.get('cn_title') for i in items]
        selected = st.selectbox("选择课题：", titles)
        it = next(i for i in items if i['cn_title'] == selected)
        
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        col_read, col_rise = st.columns(2)
        with col_read:
            st.markdown(f"""<div class="note-card"><span class="read-tag">Read (解析)</span><br><b>{it.get('cn_title')}</b><p>{it.get('cn_analysis')}</p><hr><p style='color:#64748B;'><i>{it.get('en_audio_summary')}</i></p></div>""", unsafe_allow_html=True)
        with col_rise:
            st.markdown(f"""<div class="note-card"><span class="rise-tag">Rise (领导力)</span><br><b>Case Study:</b><p>{it.get('case_study')}</p><hr><b>Reflection:</b><ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection_flow', [])])}</ul></div>""", unsafe_allow_html=True)
            if st.button("🧠 就此话题咨询教练", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"我想深入探讨关于《{it.get('cn_title')}》的管理挑战。"})
                st.session_state.page = "Coach"
                st.rerun()

elif st.session_state.page == "Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # 真正调用 DeepSeek 接口
        if DEEPSEEK_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
                payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a top-tier Executive Coach and English Trainer. Slogan: Read to Rise, Rise to Lead. Provide bilingual, actionable advice."}] + st.session_state.messages}
                res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
                ans = res.json()['choices'][0]['message']['content']
            except: ans = "教练大脑连接超时，请检查网络。"
        else: ans = "API Key 缺失，请联系管理员。"

        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
