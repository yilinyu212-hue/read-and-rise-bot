import streamlit as st
import json, os, requests

# --- 1. 基础配置与安全 ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
ADMIN_PASSWORD = "your_private_password" # 👈 修改为你自己的管理密码

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"

# --- 2. 视觉样式 (中高层审美) ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    /* 播客卡片 */
    .podcast-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 35px; border-radius: 24px; color: white; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15); border: 1px solid #334155;
    }
    .chip { padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-right: 8px; }
    .chip-read { background: #DBEAFE; color: #1E40AF; }
    .chip-rise { background: #DCFCE7; color: #166534; }
    .chip-model { background: #FEF3C7; color: #92400E; }
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .vocab-box { background: #F1F5F9; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 4px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

# --- 3. 数据处理函数 ---
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else data.get("items", [])
            except: return []
    return []

def save_json(items, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"items": items} if filename == "data.json" else items, f, ensure_ascii=False)

# --- 4. 侧边栏导航 ---
with st.sidebar:
    st.markdown("## 🏹 Read & Rise")
    st.caption("Strategic Intelligence for Educators")
    st.divider()
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    if st.button("📚 Knowledge Base", use_container_width=True): st.session_state.page = "📚 Knowledge Base"
    if st.button("🧠 AI Coach", use_container_width=True): st.session_state.page = "🧠 AI Coach"
    
    st.divider()
    with st.expander("🔐 Admin Access"):
        pwd = st.text_input("Admin Key", type="password")
        if pwd == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            if st.button("进入管理后台", use_container_width=True): st.session_state.page = "🛠 Admin Console"

# --- 5. 页面逻辑 ---

# A. 管理后台 (上传 NotebookLM 播客)
if st.session_state.page == "🛠 Admin Console" and st.session_state.authenticated:
    st.title("🛠 CMS - 内容精修与播客上传")
    items = load_json("data.json")
    if items:
        titles = [i.get('cn_title') for i in items]
        selected = st.selectbox("选择要精读优化的文章：", titles)
        idx = titles.index(selected)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎙 替换 NotebookLM 播客")
            uploaded_file = st.file_uploader("上传音频文件", type=["mp3", "wav"])
            if uploaded_file:
                audio_dir = "audio"
                if not os.path.exists(audio_dir): os.makedirs(audio_dir)
                fpath = os.path.join(audio_dir, f"nb_{idx}.mp3")
                with open(fpath, "wb") as f: f.write(uploaded_file.getbuffer())
                items[idx]['audio_file'] = fpath
                st.success("播客音频已关联！")
        
        with col2:
            st.subheader("📝 标题与摘要精修")
            items[idx]['cn_title'] = st.text_input("标题", items[idx]['cn_title'])
            items[idx]['cn_analysis'] = st.text_area("深度解析", items[idx]['cn_analysis'], height=200)

        if st.button("🚀 发布更新"):
            save_json(items, "data.json")
            st.toast("内容已同步至前台！")
    else: st.warning("请先同步数据。")

# B. 研读中心 (沉浸式播客展示)
elif st.session_state.page == "🚀 Intelligence Hub":
    items = load_json("data.json")
    if items:
        with st.sidebar:
            selected_title = st.radio("今日专栏：", [i.get('cn_title') for i in items])
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        # 沉浸式播放器视觉
        st.markdown(f"""
        <div class="podcast-card">
            <div style="display: flex; align-items: center; gap: 25px;">
                <div style="font-size: 50px; background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 20px;">🎙️</div>
                <div>
                    <div style="color: #60A5FA; font-weight: 700; letter-spacing: 1.5px; font-size: 0.8rem;">SPECIAL BRIEFING</div>
                    <div style="font-size: 1.8rem; font-weight: 700; margin: 5px 0;">{it.get('cn_title')}</div>
                    <div style="opacity: 0.7;">Deep Dive: {it.get('source_name')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown('<div class="chip chip-read">THE READ (INPUT)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-card">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
            st.markdown("#### 📚 Vocabulary Builder")
            for v in it.get('vocab_list', []):
                st.markdown(f'<div class="vocab-box"><b>{v["word"]}</b>: {v["meaning"]}<br><small>{v["usage"]}</small></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="chip chip-rise">THE RISE (GROWTH)</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="content-card">
                <p class="chip chip-model">思维模型：{it.get('mental_model')}</p>
                <p><b>实战案例：</b><br>{it.get('case_study')}</p>
                <hr><b>管理者反思：</b>
                <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection', [])])}</ul>
            </div>""", unsafe_allow_html=True)
    else: st.info("数据同步中...")

# C. Dashboard (首页)
elif st.session_state.page == "🏠 Dashboard":
    st.title("Hi, Leader! 👋")
    items = load_json("data.json")
    if items:
        for it in items:
            st.markdown(f"""<div class="content-card">
                <span class="chip chip-model">MIND MODEL: {it.get('mental_model')}</span>
                <span style="float:right; color:#94A3B8; font-size:0.8rem;">{it.get('source_name')}</span>
                <h3 style="margin:10px 0;">{it.get('cn_title')}</h3>
                <p style="color:#64748B;">{it.get('cn_analysis')[:150]}...</p>
            </div>""", unsafe_allow_html=True)

# ... (其他页面 Knowledge Base 和 Coach 逻辑保持不变) ...
