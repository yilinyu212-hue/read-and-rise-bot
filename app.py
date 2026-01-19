import streamlit as st
import json, os, requests

# --- 1. 基础配置与初始化 (解决报错的关键) ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# --- 2. 视觉样式 (标签块设计) ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .chip { padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-right: 8px; }
    .chip-read { background: #DBEAFE; color: #1E40AF; }
    .chip-rise { background: #DCFCE7; color: #166534; }
    .chip-model { background: #FEF3C7; color: #92400E; }
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px; }
    .vocab-box { background: #F1F5F9; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 4px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏导航 ---
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

# --- 4. 页面逻辑 ---

# Dashboard 页面
if st.session_state.page == "🏠 Dashboard":
    st.title("Hi, Leader! 👋")
    items = load_json("data.json")
    if items:
        for it in items:
            st.markdown(f"""<div class="content-card">
                <span class="chip chip-model">MIND MODEL: {it.get('mental_model')}</span>
                <span style="float:right; color:#94A3B8; font-size:0.8rem;">{it.get('source_name')}</span>
                <h3 style="margin:10px 0;">{it.get('cn_title')}</h3>
                <p style="color:#64748B;">{it.get('cn_analysis')[:120]}...</p>
            </div>""", unsafe_allow_html=True)
    else: st.info("正在等待 GitHub 同步数据...")

# 研读中心
elif st.session_state.page == "🚀 Intelligence Hub":
    items = load_json("data.json")
    if items:
        with st.sidebar:
            selected_title = st.radio("选择今日文章：", [i.get('cn_title') for i in items])
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        st.subheader(it.get('cn_title'))
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="chip chip-read">READ (INPUT)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-card">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
            st.markdown("#### 📚 Vocabulary Builder")
            for v in it.get('vocab_list', []):
                st.markdown(f'<div class="vocab-box"><b>{v["word"]}</b>: {v["meaning"]}<br><small>{v["usage"]}</small></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="chip chip-rise">RISE (GROWTH)</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="content-card">
                <p class="chip chip-model">思维模型：{it.get('mental_model')}</p>
                <p><b>实战案例：</b><br>{it.get('case_study')}</p>
                <hr><b>领导力反思：</b>
                <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection', [])])}</ul>
            </div>""", unsafe_allow_html=True)

# 知识库
elif st.session_state.page == "📚 Knowledge Base":
    st.title("📚 Knowledge Archive")
    history = load_json("knowledge_base.json")
    if history:
        search = st.text_input("🔍 搜索历史归档...")
        for h in history:
            if search.lower() in h['cn_title'].lower():
                with st.expander(f"📅 {h.get('date')} | {h.get('cn_title')}"):
                    st.write(h.get('cn_analysis'))
    else: st.info("暂无归档，明天更新后会自动出现。")

# AI Coach
elif st.session_state.page == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if prompt := st.chat_input("Speak with your coach..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # 这里接入你之前的 DeepSeek API 调用代码...
