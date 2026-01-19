import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 从系统环境变量获取 KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 1. 高级商务 UI 样式 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC; }
    .header-section { background: #0F172A; padding: 50px; text-align: center; color: white; border-radius: 0 0 40px 40px; }
    .slogan { font-size: 1.4rem; opacity: 0.9; font-style: italic; margin-top: 10px; font-family: 'Georgia', serif; }
    
    /* 卡片式设计 */
    .note-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 25px; border: 1px solid #E2E8F0; }
    .read-box { border-left: 6px solid #3B82F6; padding-left: 20px; margin-bottom: 20px; }
    .rise-box { border-left: 6px solid #10B981; padding-left: 20px; }
    .lang-tag { background: #EEF2FF; color: #4338CA; padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="header-section"><h1>Read & Rise</h1><div class="slogan">Read to Rise, Rise to Lead.</div></div>""", unsafe_allow_html=True)

# 状态管理
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "messages" not in st.session_state: st.session_state.messages = []
if "selected_article" not in st.session_state: st.session_state.selected_article = None

# 横向导航
n1, n2, n3 = st.columns(3)
if n1.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
if n2.button("🚀 Intelligence", use_container_width=True): st.session_state.page = "Intelligence"
if n3.button("🧠 Coach", use_container_width=True): st.session_state.page = "Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try: return json.load(f).get("items", [])
            except: return []
    return []

items = load_data()

# --- 2. 页面分发 ---

if st.session_state.page == "Dashboard":
    st.subheader("Executive Focus")
    if items:
        top = items[0]
        st.markdown(f"""<div class="note-card"><h3>🔥 Top Strategic Insight</h3><h4>{top.get('cn_title')}</h4><p>{top.get('cn_analysis')[:200]}...</p></div>""", unsafe_allow_html=True)
    else: st.warning("Syncing content...")

elif st.session_state.page == "Intelligence":
    # 侧边选择栏（模拟每篇文章一页的效果）
    if items:
        titles = [item.get('cn_title') for item in items]
        selected_title = st.selectbox("Select Insight to Study:", titles)
        current_item = next(i for i in items if i['cn_title'] == selected_title)
        
        # 文章展示主体
        st.markdown(f"## {current_item.get('cn_title')}")
        st.caption(f"Original: {current_item.get('en_title')}")
        
        if os.path.exists(current_item.get('audio_file','')): 
            st.audio(current_item['audio_file'])
        
        # 卡片笔记布局
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="note-card read-box"><h3>📚 Read (中英解析)</h3><p>{current_item.get('cn_analysis')}</p><hr/><p style='color:#64748B; font-size:0.9rem;'>{current_item.get('en_title')}</p></div>""", unsafe_allow_html=True)
            st.markdown("**Core Vocabulary**")
            for v in current_item.get('vocab_cards', []):
                st.markdown(f"<span class='lang-tag'>{v['word']}</span> {v['meaning']}", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""<div class="note-card rise-box"><h3>🚀 Rise (管理提升)</h3><strong>Management Case:</strong><p>{current_item.get('case_study')}</p><hr/><strong>Strategic Flow:</strong><ul>{''.join([f'<li>{q}</li>' for q in current_item.get('reflection_flow', [])])}</ul></div>""", unsafe_allow_html=True)
            if st.button("🧠 Ask Coach about this Article", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"I just read '{current_item.get('cn_title')}'. Based on this, can you coach me on how to lead my team through this change?"})
                st.session_state.page = "Coach"
                st.rerun()

elif st.session_state.page == "Coach":
    st.header("🧠 AI Executive Coach")
    
    # 渲染历史
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Speak with your coach..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # 真正调用 DeepSeek
        if DEEPSEEK_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "system", "content": "You are a professional Executive Coach & English Trainer. Provide actionable, bilingual guidance."}] + st.session_state.messages
                }
                res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
                ans = res.json()['choices'][0]['message']['content']
            except: ans = "Sorry, I'm having trouble connecting to the brain. Please check your API Key."
        else:
            ans = "Coach is offline. (DEEPSEEK_API_KEY not found in server environments)"

        with st.chat_message("assistant"):
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
