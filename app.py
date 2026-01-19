import streamlit as st
import json, os, requests

# ================= 1. 初始化与防御性加载 =================
st.set_page_config(page_title="Read & Rise AI Coach", layout="wide", page_icon="🏹")

def load_data():
    if not os.path.exists("data.json"):
        return {"briefs": [], "weekly_question": {"cn": "正在初始化...", "en": "Initializing..."}}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        # 兜底：防止主页因缺少 Key 崩溃
        if "weekly_question" not in d:
            d["weekly_question"] = {"cn": "面对 2026 的挑战，如何重构核心竞争力？", "en": "How to rebuild core competitiveness?"}
        return d

data = load_data()

# ================= 2. AI Coach 关联对话逻辑 =================
def call_coach(user_input, art_context=None):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    # 强制注入当前研读的文章背景
    ctx = ""
    if art_context:
        ctx = f"背景文章: {art_context['title']}\n案例: {art_context.get('case_study','')}\n反思提问: {art_context.get('reflection_flow',[])}"
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是针对下文的私教。背景内容：\n{ctx}"},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.5
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except:
        return "⚠️ Coach 暂时离线。请确保 GitHub Secrets 中的 DEEPSEEK_API_KEY 已正确配置。"

# ================= 3. 页面渲染 =================
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "🚀 全球快报"])

# --- 🏠 Dashboard (修复 KeyError) ---
if menu == "🏠 Dashboard":
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:30px;border-radius:20px;color:white;border-left:10px solid #38BDF8;">
        <h4 style="color:#38BDF8;margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size:1.5rem;font-weight:bold;margin-top:10px;">“{data['weekly_question'].get('cn')}”</p>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.metric("今日情报密度", f"{len(data.get('briefs',[]))} 篇深度洞察")

# --- 🚀 全球快报 (修复 TypeError & 实现左右同框) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    
    with col_l:
        st.header("🚀 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.container(border=True):
                st.subheader(art['title'])
                st.caption(f"源自: {art.get('source')} | 模型: {art.get('related_model')}")
                
                t1, t2, t3 = st.tabs(["📑 深度摘要", "🎙️ 词汇金句", "🔍 案例反思"])
                with t1:
                    # 修复 TypeError 的核心：判断是列表还是字符串
                    for lang, key in [("EN Summary", "en_summary"), ("中文摘要", "cn_summary")]:
                        st.write(f"**{lang}:**")
                        items = art.get(key, [])
                        if isinstance(items, list):
                            for item in items: st.write(f"• {item}")
                        else:
                            st.write(items)
                with t2:
                    for v in art.get('vocab_bank', []):
                        st.write(f"🔹 **{v['word']}**: {v['meaning']}")
                with t3:
                    st.info(f"🔍 案例分析: {art.get('case_study')}")
                    for q in art.get('reflection_flow', []): st.warning(q)
                
                if st.button("🎙️ 开启针对性对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.history = []

    with col_r:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            act = st.session_state.active_art
            st.info(f"正在深度对话：《{act['title']}》")
            
            chat_box = st.container(height=500)
            if "history" not in st.session_state: st.session_state.history = []
            
            for m in st.session_state.history:
                with chat_box.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("向教练提问..."):
                st.session_state.history.append({"role": "user", "content": p})
                with chat_box.chat_message("user"): st.markdown(p)
                with chat_box.chat_message("assistant"):
                    r = call_coach(p, act)
                    st.markdown(r)
                    st.session_state.history.append({"role": "assistant", "content": r})
        else:
            st.info("请在左侧点击【开启对话】按钮启动私教 Session。")
