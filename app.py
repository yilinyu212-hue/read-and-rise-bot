import streamlit as st
import json, os, requests

# --- 1. 基础配置与安全 (请在此修改你的管理密码) ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
ADMIN_PASSWORD = "readrise2026" # 👈 建议修改为你的私密密码

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"

# --- 2. 视觉样式 (高阶管理感设计) ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    /* 播客播放器卡片 */
    .podcast-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 35px; border-radius: 24px; color: white; margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 1px solid #334155;
    }
    .chip { padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-right: 8px; }
    .chip-read { background: #DBEAFE; color: #1E40AF; }
    .chip-rise { background: #DCFCE7; color: #166534; }
    .chip-model { background: #FEF3C7; color: #92400E; }
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .vocab-box { background: #F1F5F9; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 4px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

# --- 3. 数据加载 ---
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
    st.caption("Intelligence for Modern Educators")
    st.divider()
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    if st.button("📚 Knowledge Base", use_container_width=True): st.session_state.page = "📚 Knowledge Base"
    if st.button("🧠 AI Coach", use_container_width=True): st.session_state.page = "🧠 AI Coach"
    
    st.divider()
    with st.expander("🔐 Admin Access"):
        pwd = st.text_input("Enter Admin Key", type="password")
        if pwd == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            if st.button("Enter Admin Console", use_container_width=True): st.session_state.page = "🛠 Admin Console"

# --- 5. 页面逻辑 ---

# A. 管理后台 (上传播客)
if st.session_state.page == "🛠 Admin Console" and st.session_state.authenticated:
    st.title("🛠 Content Management System")
    items = load_json("data.json")
    if items:
        titles = [i.get('cn_title') for i in items]
        selected = st.selectbox("Select Article to Optimize:", titles)
        idx = titles.index(selected)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎙 Upload NotebookLM Podcast")
            uploaded_file = st.file_uploader("Replace default audio with high-quality podcast", type=["mp3"])
            if uploaded_file:
                if not os.path.exists("audio"): os.makedirs("audio")
                fpath = os.path.join("audio", f"podcast_{idx}.mp3")
                with open(fpath, "wb") as f: f.write(uploaded_file.getbuffer())
                items[idx]['audio_file'] = fpath
                st.success("Podcast successfully linked!")
        
        with col2:
            st.subheader("📝 Refine Content")
            items[idx]['cn_title'] = st.text_input("Title", items[idx]['cn_title'])
            items[idx]['cn_analysis'] = st.text_area("Analysis", items[idx]['cn_analysis'], height=200)

        if st.button("🚀 Publish Changes", use_container_width=True):
            save_json(items, "data.json")
            st.toast("Success! Updates are now live.")
    else: st.warning("No data found. Run crawler first.")

# B. 研读中心 (Tab 布局 + Coach 联动)
elif st.session_state.page == "🚀 Intelligence Hub":
    items = load_json("data.json")
    if items:
        with st.sidebar:
            selected_title = st.radio("Intelligence Feed:", [i.get('cn_title') for i in items])
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        # 播客 UI
        st.markdown(f"""
        <div class="podcast-card">
            <div style="display: flex; align-items: center; gap: 25px;">
                <div style="font-size: 50px; background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 20px;">🎙️</div>
                <div>
                    <div style="color: #60A5FA; font-weight: 700; letter-spacing: 1.5px; font-size: 0.75rem;">SPECIAL PODCAST BRIEFING</div>
                    <div style="font-size: 1.8rem; font-weight: 700; margin: 5px 0;">{it.get('cn_title')}</div>
                    <div style="opacity: 0.7;">Original Source: {it.get('source_name')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        # --- TAB 布局 ---
        tab1, tab2, tab3 = st.tabs(["💡 AI Insights", "🌐 Bilingual Study", "🧠 Consult Coach"])
        
        with tab1:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown('<div class="chip chip-read">READ / 核心解析</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="content-card">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
                st.markdown("#### 📚 Vocabulary Builder")
                for v in it.get('vocab_list', []):
                    st.markdown(f'<div class="vocab-box"><b>{v["word"]}</b>: {v["meaning"]}<br><small>{v["usage"]}</small></div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="chip chip-rise">RISE / 认知跃迁</div>', unsafe_allow_html=True)
                st.markdown(f"""<div class="content-card">
                    <p class="chip chip-model">思维模型：{it.get('mental_model')}</p>
                    <p><b>实战案例：</b><br>{it.get('case_study')}</p>
                    <hr><b>领导力反思：</b>
                    <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection', [])])}</ul>
                </div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown("### 🌐 中英对照研读 (Original vs. Analysis)")
            st.info("对于追求极致准确性的研读，建议对比原文段落。")
            st.write("**[Original English Summary]**")
            st.write(it.get('en_summary'))
            st.divider()
            st.write("**[中文深度解析]**")
            st.write(it.get('cn_analysis'))

        with tab3:
            st.subheader("🧠 针对本篇咨询 AI Coach")
            st.write(f"Coach 已准备好讨论《{it.get('cn_title')}》及其背后的【{it.get('mental_model')}】模型。")
            coach_prompt = f"关于文章《{it.get('cn_title')}》，我想探讨【{it.get('mental_model')}】如何指导我的团队管理？"
            if st.button("🚀 开启深度咨询对话"):
                st.session_state.messages.append({"role": "user", "content": coach_prompt})
                st.session_state.page = "🧠 AI Coach"
                st.rerun()

# C. 其他基础页面 (Dashboard, Coach)
elif st.session_state.page == "🏠 Dashboard":
    st.title("Hi, Leader! 👋")
    items = load_json("data.json")
    for it in items:
        st.markdown(f"""<div class="content-card">
            <span class="chip chip-model">MODEL: {it.get('mental_model')}</span>
            <span style="float:right; color:#94A3B8; font-size:0.8rem;">{it.get('source_name')}</span>
            <h3 style="margin:10px 0;">{it.get('cn_title')}</h3>
            <p style="color:#64748B;">{it.get('cn_analysis')[:130]}...</p>
        </div>""", unsafe_allow_html=True)

elif st.session_state.page == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if prompt := st.chat_input("Speak with your coach..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # DeepSeek API 请求...
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json={
            "model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a Mentor for Leaders."}] + st.session_state.messages
        })
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
