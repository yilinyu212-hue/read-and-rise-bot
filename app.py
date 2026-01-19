import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 修复 AttributeError: st.session_state 报错 ---
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "Dashboard"

# --- 视觉升级：标签块与清新风格 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    
    /* 标签块样式 */
    .tag-blue { background: #DBEAFE; color: #1E40AF; padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; }
    .tag-green { background: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; }
    .tag-purple { background: #F3E8FF; color: #6B21A8; padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; }
    
    /* 内容卡片 */
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 4px 15px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .model-badge { background: #F1F5F9; border-left: 4px solid #3B82F6; padding: 10px 15px; font-weight: 600; color: #1E293B; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# 侧边栏导航
with st.sidebar:
    st.markdown("## 🏹 Read & Rise")
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "Intelligence"
    if st.button("🧠 Coach AI", use_container_width=True): st.session_state.page = "Coach"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try: return json.load(f).get("items", [])
            except: return []
    return []

items = load_data()

# --- 页面逻辑 ---
if st.session_state.page == "Dashboard":
    st.title("Hi, Leader! 👋")
    st.info("您的思维深度决定了您的高度。以下是今日为您同步的全球洞察：")
    if items:
        for it in items:
            with st.container():
                st.markdown(f"""<div class="content-card">
                    <span class="tag-purple">MIND MODEL: {it.get('mental_model')}</span>
                    <h3 style="margin-top:10px;">{it.get('cn_title')}</h3>
                    <p style="color:#64748B;">{it.get('cn_analysis')[:120]}...</p>
                </div>""", unsafe_allow_html=True)

elif st.session_state.page == "Intelligence":
    if items:
        with st.sidebar:
            st.divider()
            selected_title = st.radio("选择文章进行深度研读：", [i.get('cn_title') for i in items])
        
        it = next(i for i in items if i['cn_title'] == selected_title)
        
        st.subheader(it.get('cn_title'))
        if os.path.exists(it.get('audio_file','')): 
            st.write("🎧 **Leadership Audio Briefing (Long Version)**")
            st.audio(it['audio_file'])
        
        # 交叉关联：思维模型
        st.markdown(f'<div class="model-badge">核心思维模型：{it.get("mental_model")}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(f'<span class="tag-blue">READ (INPUT)</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-card">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
            
            # 词汇总结卡片
            st.markdown(f'<span class="tag-blue">VOCABULARY BUILDER</span>', unsafe_allow_html=True)
            vocab_html = "".join([f"<li><b>{v['word']}</b>: {v['meaning']}<br><small><i>{v['usage']}</i></small></li>" for v in it.get('vocab_list', [])])
            st.markdown(f'<div class="content-card"><ul>{vocab_html}</ul></div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown(f'<span class="tag-green">RISE (GROWTH)</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-card"><b>实战案例：</b><p>{it.get("case_study")}</p><hr><b>反思练习：</b><ul>{"".join([f"<li>{r}</li>" for r in it.get("reflection", [])])}</ul></div>', unsafe_allow_html=True)
            if st.button("🧠 针对此模型咨询 Coach", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": f"我想深入探讨《{it.get('cn_title')}》背后的【{it.get('mental_model')}】模型。"})
                st.session_state.page = "Coach"
                st.rerun()

elif st.session_state.page == "Coach":
    st.header("🧠 AI Executive Coach")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Speak with your coach..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # DeepSeek 调用逻辑 (省略重复代码)
