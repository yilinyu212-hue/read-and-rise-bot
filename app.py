import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- UI 视觉：打造卡片呼吸感 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC; }
    .header-section { background: #0F172A; padding: 40px; text-align: center; color: white; border-radius: 0 0 30px 30px; }
    .slogan { font-size: 1.3rem; opacity: 0.8; font-style: italic; margin-top: 10px; font-family: 'Georgia', serif; }
    
    /* 卡片笔记样式 */
    .note-card { background: white; padding: 30px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.04); margin-bottom: 25px; border: 1px solid #E5E7EB; }
    .read-tag { color: #3B82F6; font-weight: bold; font-size: 1.5rem; margin-bottom: 10px; display: block; }
    .rise-tag { color: #10B981; font-weight: bold; font-size: 1.5rem; margin-bottom: 10px; display: block; }
    .en-sub { color: #64748B; font-size: 0.95rem; line-height: 1.6; font-style: italic; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="header-section"><h1>Read & Rise</h1><div class="slogan">Read to Rise, Rise to Lead.</div></div>""", unsafe_allow_html=True)

# 页面状态
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "messages" not in st.session_state: st.session_state.messages = []

# 横向导航按钮
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

# --- 1. Dashboard ---
if st.session_state.page == "Dashboard":
    if items:
        top = items[0]
        st.markdown(f"""<div class="note-card">
            <h2 style='text-align:center;'>今日首荐：{top.get('cn_title')}</h2>
            <p style='text-align:center;'>{top.get('cn_analysis')[:150]}...</p>
        </div>""", unsafe_allow_html=True)
    else: st.info("正在为您从全球智库同步内容...")

# --- 2. Intelligence (左右分栏卡片式阅读) ---
elif st.session_state.page == "Intelligence":
    if items:
        # 下拉框实现“每篇一页”的专注感
        titles = [i.get('cn_title') for i in items]
        selected = st.selectbox("选择今日研读课题：", titles)
        it = next(i for i in items if i['cn_title'] == selected)
        
        # 音频播放
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        col_read, col_rise = st.columns(2, gap="large")
        
        with col_read:
            st.markdown(f"""<div class="note-card">
                <span class="read-tag">Read.</span>
                <p><b>{it.get('cn_title')}</b></p>
                <p>{it.get('cn_analysis')}</p>
                <hr>
                <p class="en-sub"><b>English Summary:</b><br>{it.get('en_summary', 'N/A')}</p>
            </div>""", unsafe_allow_html=True)
            st.markdown("🔹 **地道表达 (Language Edge)**")
            for v in it.get('vocab_cards', []):
                st.write(f"**{v['word']}**: {v['meaning']}")

        with col_rise:
            st.markdown(f"""<div class="note-card">
                <span class="rise-tag">Rise.</span>
                <p><b>Executive Case Study:</b></p>
                <p>{it.get('case_study')}</p>
                <hr>
                <p><b>Reflection for Leaders:</b></p>
                <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection_flow', [])])}</ul>
            </div>""", unsafe_allow_html=True)
            if st.button("🧠 针对此议题向教练提问", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"我想针对《{it.get('cn_title')}》这篇文章探讨我的管理难题。"})
                st.session_state.page = "Coach"
                st.rerun()

# --- 3. Coach (真正打通 DeepSeek) ---
elif st.session_state.page == "Coach":
    st.header("🧠 Executive Coaching Session")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # 真正调用接口
        if DEEPSEEK_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "system", "content": "You are a professional Executive Coach & English Trainer. Slogan: Read to Rise, Rise to Lead. Provide bilingual and actionable advice."}] + st.session_state.messages
                }
                res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
                ans = res.json()['choices'][0]['message']['content']
            except: ans = "抱歉，教练大脑连接超时，请检查服务器网络。"
        else: ans = "API Key 尚未配置。"

        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
