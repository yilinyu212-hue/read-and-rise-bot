import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- UI 视觉：清新商务风 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F0F2F6; }
    
    /* 去掉黑底，改用极简白色 Header */
    .header-section { 
        background: white; 
        padding: 40px; 
        text-align: center; 
        border-radius: 0 0 40px 40px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    .main-title { color: #1E293B; font-size: 3rem; font-weight: 800; margin: 0; }
    .slogan { color: #64748B; font-size: 1.3rem; font-style: italic; margin-top: 5px; }
    
    /* 卡片呼吸感 */
    .note-card { background: white; padding: 30px; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; margin-bottom: 25px; }
    .card-title { color: #0F172A; font-size: 1.8rem; font-weight: 700; margin-bottom: 15px; }
    .section-tag { color: #3B82F6; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# 清新版 Header
st.markdown("""
<div class="header-section">
    <h1 class="main-title">Read & Rise</h1>
    <div class="slogan">Read to Rise, Rise to Lead.</div>
</div>
""", unsafe_allow_html=True)

# 状态与导航
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "messages" not in st.session_state: st.session_state.messages = []

n1, n2, n3 = st.columns(3)
if n1.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
if n2.button("🚀 Intelligence", use_container_width=True): st.session_state.page = "Intelligence"
if n3.button("🧠 AI Coach", use_container_width=True): st.session_state.page = "Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try: return json.load(f).get("items", [])
            except: return []
    return []

items = load_data()

# --- 1. Dashboard (Hi, Leaders! 回归) ---
if st.session_state.page == "Dashboard":
    st.markdown("### Hi, Leaders! 👋")
    if items:
        top = items[0]
        st.markdown(f"""<div class="note-card">
            <div class="section-tag">Featured Insight</div>
            <div class="card-title">{top.get('cn_title')}</div>
            <p style='color: #475569;'>{top.get('cn_analysis')[:200]}...</p>
        </div>""", unsafe_allow_html=True)
    else: st.info("Intelligence is being curated...")

# --- 2. Intelligence (左右分屏卡片) ---
elif st.session_state.page == "Intelligence":
    if items:
        titles = [i.get('cn_title') for i in items]
        selected = st.selectbox("Select Study Item:", titles)
        it = next(i for i in items if i['cn_title'] == selected)
        
        if os.path.exists(it.get('audio_file','')): 
            st.write("🎧 **Leadership Audio Briefing (Long Version)**")
            st.audio(it['audio_file'])
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(f"""<div class="note-card">
                <div class="section-tag" style="color:#2563EB;">📚 Read (Input)</div>
                <div style="font-size:1.2rem; font-weight:600; margin:10px 0;">{it.get('cn_title')}</div>
                <p>{it.get('cn_analysis')}</p>
                <hr style="border:0.5px solid #F1F5F9;">
                <p style="color:#64748B; font-size:0.9rem; font-style:italic;"><b>Audio Script:</b> {it.get('en_summary')}</p>
            </div>""", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""<div class="note-card">
                <div class="section-tag" style="color:#059669;">🚀 Rise (Growth)</div>
                <div style="font-size:1.2rem; font-weight:600; margin:10px 0;">Case Study</div>
                <p>{it.get('case_study')}</p>
                <hr style="border:0.5px solid #F1F5F9;">
                <div class="section-tag" style="color:#059669;">Reflection</div>
                <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection_flow', [])])}</ul>
            </div>""", unsafe_allow_html=True)
            if st.button("🧠 Consult with AI Coach", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"Let's discuss: {it.get('cn_title')}"})
                st.session_state.page = "Coach"
                st.rerun()

# --- 3. Coach (深度对话) ---
elif st.session_state.page == "Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask about leadership or language..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        if DEEPSEEK_API_KEY:
            headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a mentor for educators and leaders. Provide deep, actionable coaching."}] + st.session_state.messages}
            res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
            ans = res.json()['choices'][0]['message']['content']
        else: ans = "Brain offline (API Key Missing)."

        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
