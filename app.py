import streamlit as st
import json, os, requests

# ================= 1. 配置与专业美化 =================
st.set_page_config(page_title="Read & Rise AI Coach", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .coach-card { 
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
        padding: 30px; border-radius: 20px; color: white; 
        border-left: 10px solid #38BDF8; margin-bottom: 25px;
    }
    .status-badge { background: #E0F2FE; color: #0369A1; padding: 4px 12px; border-radius: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"):
        return {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "加载中", "en": "Loading"}}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ================= 2. AI 教练逻辑 (打通关联) =================
def call_coach_api(prompt, art_context=None):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    # 强制将当前文章内容作为上下文
    context = ""
    if art_context:
        context = f"你目前正在陪同用户阅读《{art_context['title']}》。\n案例: {art_context.get('case_study','')}\n反思: {art_context.get('reflection_flow',[])}"
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是一个专业的 AI Coach。背景知识：{context}"},
                    {"role": "user", "content": prompt}
                ], "temperature": 0.4
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except: return "Coach 正在深思，请检查 API 密钥。建议：您可以在本地设置环境变量以确保连接。"

# ================= 3. 页面渲染 =================
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "🚀 全球快报"])

# --- 🏠 主页 Dashboard (恢复显示) ---
if menu == "🏠 Dashboard":
    st.markdown(f"""<div class="coach-card">
        <h4 style="color: #38BDF8; margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size: 1.1rem; color: #94A3B8; font-style: italic; margin-top:15px;">"{data.get('weekly_question', {}).get('en', '')}"</p>
        <p style="font-size: 1.5rem; font-weight: bold; margin-top:5px;">“{data.get('weekly_question', {}).get('cn', '思考中...')}”</p>
    </div>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("今日捕获", f"{len(data.get('briefs', []))} 篇")
    c2.metric("深度建模", f"{len(data.get('deep_articles', []))} 篇")
    c3.metric("智库源", "12 个")

# --- 🚀 全球快报 (左阅读，右对话) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    
    with col_l:
        st.header("🚀 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.container(border=True):
                st.subheader(art['title'])
                st.markdown(f"<span class='status-badge'>{art.get('source')}</span> <span class='status-badge'>模型: {art.get('related_model')}</span>", unsafe_allow_html=True)
                
                t1, t2, t3 = st.tabs(["深度摘要", "管理词汇", "案例反思"])
                with t1:
                    # 修复列表连接报错的代码
                    st.write("**EN Summary:**")
                    summaries = art.get('en_summary', [])
                    if isinstance(summaries, list):
                        for s in summaries: st.write(f"• {s}")
                    else: st.write(summaries)
                    
                    st.write("**中文摘要:**")
                    cn_summaries = art.get('cn_summary', [])
                    if isinstance(cn_summaries, list):
                        for s in cn_summaries: st.write(f"• {s}")
                    else: st.write(cn_summaries)
                with t2:
                    for v in art.get('vocab_bank', []):
                        st.write(f"🔹 **{v['word']}**: {v['meaning']}")
                        st.caption(f"Example: {v['example']}")
                with t3:
                    st.info(f"🔍 **案例解析:** {art.get('case_study')}")
                    for q in art.get('reflection_flow', []): st.warning(q)
                
                if st.button("🎙️ 针对此文开启对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.chat_history = []

    with col_r:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            act = st.session_state.active_art
            st.markdown(f"**正在研读：** {act['title']}")
            
            chat_container = st.container(height=500)
            if "chat_history" not in st.session_state: st.session_state.chat_history = []
            
            for m in st.session_state.chat_history:
                with chat_container.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("向教练提问..."):
                st.session_state.chat_history.append({"role": "user", "content": p})
                with chat_container.chat_message("user"): st.markdown(p)
                with chat_container.chat_message("assistant"):
                    resp = call_coach_api(p, act)
                    st.markdown(resp)
                    st.session_state.chat_history.append({"role": "assistant", "content": resp})
        else:
            st.info("请在左侧点击按钮，开启针对性教练 Session")
