import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 状态初始化 ---
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"

# --- UI 视觉 CSS ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    
    /* 标签块样式 */
    .chip { padding: 5px 12px; border-radius: 8px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-right: 8px; }
    .chip-read { background: #DBEAFE; color: #1E40AF; }
    .chip-rise { background: #DCFCE7; color: #166534; }
    .chip-model { background: #FEF3C7; color: #92400E; }
    
    /* 卡片设计 */
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; }
    .vocab-box { background: #F1F5F9; padding: 15px; border-radius: 12px; border-left: 5px solid #3B82F6; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 侧边栏导航 ---
with st.sidebar:
    st.markdown("## 🏹 Read & Rise")
    st.caption("Read to Rise, Rise to Lead.")
    st.divider()
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    if st.button("📚 Knowledge Base", use_container_width=True): st.session_state.page = "📚 Knowledge Base"
    if st.button("🧠 AI Coach", use_container_width=True): st.session_state.page = "🧠 AI Coach"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res if isinstance(res, list) else res.get("items", [])
            except: return []
    return []

# --- 逻辑展示 ---

if st.session_state.page == "🏠 Dashboard":
    st.title("Hi, Leader! 👋")
    items = load_json("data.json")
    if items:
        st.info(f"今日为您同步了来自 {len(items)} 个顶级源的洞察。")
        for it in items:
            st.markdown(f"""<div class="content-card">
                <span class="chip chip-model">MIND MODEL: {it.get('mental_model')}</span>
                <span style="float:right; color:#94A3B8; font-size:0.8rem;">Source: {it.get('source_name')}</span>
                <h3 style="margin:10px 0;">{it.get('cn_title')}</h3>
                <p style="color:#64748B;">{it.get('cn_analysis')[:150]}...</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("内容正在同步中，请稍后...")

elif st.session_state.page == "🚀 Intelligence Hub":
    items = load_json("data.json")
    if items:
        with st.sidebar:
            st.divider()
            selected_title = st.radio("选择今日研读：", [i.get('cn_title') for i in items])
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        st.subheader(it.get('cn_title'))
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown('<div class="chip chip-read">READ (INPUT)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-card">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
            
            st.markdown("#### 📚 Vocabulary Builder")
            for v in it.get('vocab_list', []):
                st.markdown(f"""<div class="vocab-box"><b>{v['word']}</b>: {v['meaning']}<br><small><i>{v['usage']}</i></small></div>""", unsafe_allow_html=True)
                
        with c2:
            st.markdown('<div class="chip chip-rise">RISE (GROWTH)</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="content-card">
                <p class="chip chip-model">思维模型：{it.get('mental_model')}</p>
                <p><b>实战案例：</b><br>{it.get('case_study')}</p>
                <hr>
                <b>领导力反思练习：</b>
                <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection', [])])}</ul>
            </div>""", unsafe_allow_html=True)
            if st.button("🧠 针对此内容咨询 Coach", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"关于《{it.get('cn_title')}》提到的【{it.get('mental_model')}】模型，我想探讨一下。"})
                st.session_state.page = "🧠 AI Coach"
                st.rerun()

elif st.session_state.page == "📚 Knowledge Base":
    st.title("📚 Knowledge Archive")
    history = load_json("knowledge_base.json")
    if history:
        search = st.text_input("🔍 搜索历史洞察 (标题或模型)...")
        for h in history:
            if search.lower() in h['cn_title'].lower() or search.lower() in h.get('mental_model','').lower():
                with st.expander(f"📅 {h.get('date')} | {h.get('cn_title')}"):
                    st.write(f"**思维模型:** {h.get('mental_model')}")
                    st.write(h.get('cn_analysis'))
                    st.caption(f"Source: {h.get('source_name')}")
    else:
        st.info("暂无归档内容，系统会在每日自动运行后开始积累。")

elif st.session_state.page == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        if DEEPSEEK_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
                payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are a professional Executive Coach."}] + st.session_state.messages}
                res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
                ans = res.json()['choices'][0]['message']['content']
            except: ans = "Connection error."
        else: ans = "API Key not found."
        
        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
