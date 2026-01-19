import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- UI 视觉：清新明亮的教育/商务风 ---
st.markdown("""
<style>
    /* 侧边栏背景色 */
    [data-testid="stSidebar"] { background-color: #F8FAFC; border-right: 1px solid #E2E8F0; }
    .stApp { background-color: #FFFFFF; }
    
    /* 顶部导航去掉黑底 */
    .nav-container { background: white; padding: 20px; border-bottom: 1px solid #F1F5F9; margin-bottom: 20px; }
    .main-title { color: #0F172A; font-size: 2.2rem; font-weight: 800; text-align: center; margin:0; }
    .slogan { color: #64748B; text-align: center; font-style: italic; font-size: 1rem; }

    /* 卡片样式 */
    .note-card { background: #FFFFFF; padding: 30px; border-radius: 16px; border: 1px solid #F1F5F9; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px; }
    .read-header { color: #2563EB; font-weight: 800; font-size: 1.4rem; border-bottom: 2px solid #DBEAFE; padding-bottom: 8px; margin-bottom: 15px; }
    .rise-header { color: #059669; font-weight: 800; font-size: 1.4rem; border-bottom: 2px solid #DCFCE7; padding-bottom: 8px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# 顶部导航渲染
st.markdown('<div class="nav-container"><h1 class="main-title">Read & Rise</h1><div class="slogan">Read to Rise, Rise to Lead.</div></div>', unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"

# 侧边栏导航
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3429/3429149.png", width=80)
    st.markdown("### Menu")
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    if st.button("🧠 AI Coach", use_container_width=True): st.session_state.page = "🧠 AI Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res.get("items", [])
            except: return []
    return []

items = load_data()

# --- 页面内容 ---

if st.session_state.page == "🏠 Dashboard":
    st.markdown("### Hi, Leaders! 👋")
    st.info("欢迎回到您的私人智库。今天我们为您准备了来自 HBR、McKinsey 等渠道的深度洞察。")
    if items:
        with st.expander("📌 今日速览", expanded=True):
            for i, it in enumerate(items):
                st.write(f"{i+1}. {it.get('cn_title')}")

elif st.session_state.page == "🚀 Intelligence Hub":
    if items:
        # 左侧边栏增加文章选择列表，模拟“分页”
        with st.sidebar:
            st.divider()
            st.markdown("### 📚 Select Article")
            titles = [i.get('cn_title') for i in items]
            selected_title = st.radio("Choose to Read:", titles)
        
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        st.subheader(it.get('cn_title'))
        if os.path.exists(it.get('audio_file','')): 
            st.caption("🎧 Leadership Audio Briefing (Ryan, UK)")
            st.audio(it['audio_file'])
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(f"""<div class="note-card">
                <div class="read-header">Read (Input)</div>
                <p style="line-height:1.8;">{it.get('cn_analysis')}</p>
                <hr style="opacity:0.2">
                <p style="color:#64748B; font-size:0.9rem;"><b>Audio Script:</b> {it.get('en_summary')}</p>
            </div>""", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""<div class="note-card">
                <div class="rise-header">Rise (Cognition)</div>
                <b>Management Case Study:</b>
                <p>{it.get('case_study')}</p>
                <hr style="opacity:0.2">
                <b>Leadership Reflection:</b>
                <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection_flow', [])])}</ul>
            </div>""", unsafe_allow_html=True)
            if st.button("🧠 就此议题开启 Coach 对话", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"关于《{it.get('cn_title')}》，我想进行深度对话。"})
                st.session_state.page = "🧠 AI Coach"
                st.rerun()

elif st.session_state.page == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Speak with your mentor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        if DEEPSEEK_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
                payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a mentor for leaders. Provide deep, bilingual advice."}] + st.session_state.messages}
                res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
                ans = res.json()['choices'][0]['message']['content']
            except: ans = "Brain offline..."
        else: ans = "API Key error."

        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
