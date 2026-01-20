import streamlit as st
import json, os, requests

# --- 1. 基础配置与安全强制初始化 ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 必须在最开头初始化，防止 AttributeError
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"
if "authenticated" not in st.session_state: st.session_state.authenticated = False

ADMIN_PASSWORD = "your_password" # 👈 建议改为你自己的密码

# --- 2. 视觉样式 (管理者审美) ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .podcast-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 30px; border-radius: 20px; color: white; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15); border: 1px solid #334155;
    }
    .chip { padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-right: 8px; }
    .chip-read { background: #DBEAFE; color: #1E40AF; }
    .chip-rise { background: #DCFCE7; color: #166534; }
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 数据处理函数 ---
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res if isinstance(res, list) else res.get("items", [])
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
            if st.button("Open CMS"): st.session_state.page = "🛠 Admin"

# --- 5. 核心逻辑 ---
items = load_data()

# A. 管理员后台：上传 NotebookLM
if st.session_state.page == "🛠 Admin" and st.session_state.authenticated:
    st.title("🛠 CMS - NotebookLM 音频管理")
    if items:
        selected = st.selectbox("选择要替换播客的文章", [i['cn_title'] for i in items])
        idx = [i['cn_title'] for i in items].index(selected)
        file = st.file_uploader("上传 NotebookLM MP3", type=["mp3"])
        if file:
            if not os.path.exists("audio"): os.makedirs("audio")
            path = f"audio/podcast_{idx}.mp3"
            with open(path, "wb") as f: f.write(file.getbuffer())
            items[idx]['audio_file'] = path
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump({"items": items}, f, ensure_ascii=False)
            st.success("播客上传成功并已关联！")

# B. 研读中心：中英对照 + 沉浸播客
elif st.session_state.page == "🚀 Intelligence Hub":
    if items:
        with st.sidebar:
            sel = st.radio("文章列表", [i['cn_title'] for i in items])
        it = next(i for i in items if i['cn_title'] == sel)
        
        # 播客 UI
        st.markdown(f'<div class="podcast-card">🎙️ <small>SPECIAL PODCAST</small><h2>{it["cn_title"]}</h2></div>', unsafe_allow_html=True)
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        # TAB 切换
        t1, t2, t3 = st.tabs(["💡 AI 洞察", "🌐 中英对照", "🧠 咨询 Coach"])
        with t1:
            st.markdown(f'<div class="content-card"><h4>核心深度解析</h4>{it["cn_analysis"]}</div>', unsafe_allow_html=True)
        with t2:
            st.markdown("### 🌐 Bilingual Study")
            col_en, col_cn = st.columns(2)
            col_en.info(f"**English Original:**\n\n{it.get('en_summary')}")
            col_cn.success(f"**中文深度解析:**\n\n{it.get('cn_analysis')}")
        with t3:
            st.subheader("🧠 与 Coach 互动")
            if st.button(f"就《{it['cn_title']}》开启咨询"):
                st.session_state.messages.append({"role": "user", "content": f"关于文章《{it['cn_title']}》，我想探讨一下具体的落地建议。"})
                st.session_state.page = "🧠 AI Coach"
                st.rerun()

# C. 首页 Dashboard
elif st.session_state.page == "🏠 Dashboard":
    st.title("Hi, Leader! 👋")
    for it in items:
        st.markdown(f"""<div class="content-card">
            <span class="chip chip-rise">Model: {it.get('mental_model')}</span>
            <h3 style="margin:10px 0;">{it.get('cn_title')}</h3>
            <p style="color:#64748B;">{it.get('cn_analysis')[:150]}...</p>
        </div>""", unsafe_allow_html=True)

# D. AI Coach 页面保持之前的对话逻辑即可...
