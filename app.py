import streamlit as st
import json, os, requests

# --- 1. 强制初始化与安全配置 ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 解决 AttributeError 的核心：必须在程序最开始初始化 session_state
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"
if "authenticated" not in st.session_state: st.session_state.authenticated = False

ADMIN_PASSWORD = "readrise2026" # 👈 请修改此密码

# --- 2. 视觉样式 (管理者审美) ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .podcast-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 30px; border-radius: 20px; color: white; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); border: 1px solid #334155;
    }
    .chip { padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-right: 8px; }
    .chip-read { background: #DBEAFE; color: #1E40AF; }
    .chip-rise { background: #DCFCE7; color: #166534; }
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 数据处理 ---
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f).get("items", []) if filename == "data.json" else json.load(f)
            except: return []
    return []

# --- 4. 侧边栏 ---
with st.sidebar:
    st.markdown("## 🏹 Read & Rise")
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    if st.button("🧠 AI Coach", use_container_width=True): st.session_state.page = "🧠 AI Coach"
    
    st.divider()
    with st.expander("🔐 Admin Access"):
        pwd = st.text_input("Key", type="password")
        if pwd == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            if st.button("Enter Admin Console"): st.session_state.page = "🛠 Admin"

# --- 5. 页面逻辑 ---

# A. 管理后台：手动上传 NotebookLM 播客
if st.session_state.page == "🛠 Admin" and st.session_state.authenticated:
    st.title("🛠 CMS - NotebookLM 播客上传")
    items = load_json("data.json")
    if items:
        selected = st.selectbox("选择要替换播客的文章：", [i['cn_title'] for i in items])
        idx = [i['cn_title'] for i in items].index(selected)
        file = st.file_uploader("上传 NotebookLM MP3", type=["mp3"])
        if file:
            path = f"audio/custom_{idx}.mp3"
            if not os.path.exists("audio"): os.makedirs("audio")
            with open(path, "wb") as f: f.write(file.getbuffer())
            items[idx]['audio_file'] = path
            with open("data.json", "w", encoding="utf-8") as f: json.dump({"items": items}, f, ensure_ascii=False)
            st.success("播客已成功替换！")

# B. 研读中心：中英对照 + 沉浸式 UI + Coach 联动
elif st.session_state.page == "🚀 Intelligence Hub":
    items = load_json("data.json")
    if items:
        with st.sidebar:
            selected_title = st.radio("Intelligence Feed:", [i['cn_title'] for i in items])
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        st.markdown(f'<div class="podcast-card">🎙️ <small>SPECIAL BRIEFING</small><br><h2>{it["cn_title"]}</h2></div>', unsafe_allow_html=True)
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        tab1, tab2, tab3 = st.tabs(["💡 AI Insights", "🌐 Bilingual (中英对照)", "🧠 Coach Interaction"])
        with tab1:
            st.markdown(f'<div class="content-card"><h4>核心深度解析</h4>{it["cn_analysis"]}</div>', unsafe_allow_html=True)
        with tab2:
            st.subheader("🌐 中英对照研读")
            c1, c2 = st.columns(2)
            c1.markdown(f"**English Original:**\n\n{it.get('en_summary')}")
            c2.markdown(f"**中文深度解析:**\n\n{it.get('cn_analysis')}")
        with tab3:
            st.subheader("🧠 咨询 AI Coach")
            if st.button(f"针对《{it['cn_title']}》向 Coach 提问"):
                st.session_state.messages.append({"role": "user", "content": f"基于这篇文章，我想探讨一下【{it.get('mental_model')}】。"})
                st.session_state.page = "🧠 AI Coach"
                st.rerun()

# C. AI Coach 页面
elif st.session_state.page == "🧠 AI Coach":
    st.title("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if prompt := st.chat_input("Speak to your coach..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # 这里集成 DeepSeek API 请求逻辑...
