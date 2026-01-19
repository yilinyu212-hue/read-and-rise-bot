import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 初始化 Session State 防止报错
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"

# --- 视觉升级：高端教育培训感 ---
st.markdown("""
<style>
    .stApp { background-color: #FDFDFD; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #F0F2F6; }
    
    /* 标签块样式 */
    .tag-chip { padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-bottom: 10px; }
    .tag-read { background: #EEF2FF; color: #4338CA; }
    .tag-rise { background: #ECFDF5; color: #065F46; }
    .tag-model { background: #FFF7ED; color: #9A3412; }
    
    /* 卡片设计 */
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #F0F2F6; box-shadow: 0 4px 20px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .vocab-item { background: #F8FAFC; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 3px solid #6366F1; }
</style>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### 🏹 Read & Rise")
    st.caption("Read to Rise, Rise to Lead.")
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    if st.button("🧠 AI Coach", use_container_width=True): st.session_state.page = "🧠 AI Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try: return json.load(f).get("items", [])
            except: return []
    return []

items = load_data()

# --- 1. Dashboard ---
if st.session_state.page == "🏠 Dashboard":
    st.markdown("## Hi, Leaders! 👋")
    st.write("今日已为您更新 **10** 篇全球顶级管理内参。")
    if items:
        for it in items:
            with st.container():
                st.markdown(f"""<div class="content-card">
                    <span class="tag-chip tag-model">模型：{it.get('mental_model')}</span>
                    <span style="float:right; font-size:0.8rem; color:#94A3B8;">源：{it.get('source_name')}</span>
                    <h4 style="margin-top:0;">{it.get('cn_title')}</h4>
                    <p style="color:#64748B; font-size:0.9rem;">{it.get('cn_analysis')[:120]}...</p>
                </div>""", unsafe_allow_html=True)

# --- 2. Intelligence (分页研读) ---
elif st.session_state.page == "🚀 Intelligence Hub":
    if items:
        with st.sidebar:
            st.divider()
            st.write("📑 **研读清单**")
            selected_title = st.radio("选择课题", [i.get('cn_title') for i in items])
        
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        st.subheader(it.get('cn_title'))
        if os.path.exists(it.get('audio_file','')): st.audio(it['audio_file'])
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            # READ 模块
            st.markdown('<div class="tag-chip tag-read">READ / 输入</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-card">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
            
            # 词汇总结
            st.markdown('**📚 Vocabulary Builder**')
            for v in it.get('vocab_list', []):
                st.markdown(f"""<div class="vocab-item">
                    <b>{v['word']}</b>: {v['meaning']}<br><small><i>{v['usage']}</i></small>
                </div>""", unsafe_allow_html=True)
            
        with col2:
            # RISE 模块
            st.markdown('<div class="tag-chip tag-rise">RISE / 跃迁</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="content-card">
                <p class="tag-chip tag-model">思维模型：{it.get('mental_model')}</p>
                <p><b>实战案例：</b><br>{it.get('case_study')}</p>
                <hr><b>领导力反思：</b>
                <ul>{''.join([f'<li>{r}</li>' for r in it.get('reflection', [])])}</ul>
            </div>""", unsafe_allow_html=True)
            
            if st.button("🧠 向 AI 教练咨询该议题", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"关于《{it.get('cn_title')}》这篇文章提到的【{it.get('mental_model')}】模型，我有疑惑..."})
                st.session_state.page = "🧠 AI Coach"
                st.rerun()

# --- 3. Coach 频道 ---
elif st.session_state.page == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("输入您的问题或管理困惑..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # 实时请求 DeepSeek API
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json={
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": "You are a Mentor for Leaders."}] + st.session_state.messages
        })
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
