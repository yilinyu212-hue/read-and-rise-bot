import streamlit as st
import json, os, requests

# ================= 1. 配置与初始化 =================
st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

def load_data():
    if not os.path.exists("data.json"): return {"briefs": []}
    with open("data.json", "r", encoding="utf-8") as f: return json.load(f)

data = load_data()

# ================= 2. AI 对话引擎 (RAG) =================
def call_coach(user_input, article_context):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    context_str = f"文章标题: {article_context['title']}\n案例: {article_context.get('case_study','')}\n反思: {article_context.get('reflection_flow',[])}"
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是针对下文的私教。下文内容如下：\n{context_str}"},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.5
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except: return "Coach 正在深思，请检查 API Key 配置。"

# ================= 3. UI 布局 =================
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "🚀 全球快报"])

if menu == "🚀 全球快报":
    col_left, col_right = st.columns([0.6, 0.4]) # 左侧阅读，右侧对话

    with col_left:
        st.header("🚀 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📌 [{art.get('source')}] {art['title']}", expanded=(i==0)):
                tab1, tab2, tab3 = st.tabs(["📑 深度摘要", "🎙️ 词汇金句", "🔍 案例反思"])
                with tab1:
                    st.write("**EN Summary:**")
                    for p in art.get('en_summary', []): st.write(f"• {p}")
                    st.write("**中文摘要:**")
                    for p in art.get('cn_summary', []): st.write(f"• {p}")
                with tab2:
                    for v in art.get('vocab_bank', []):
                        st.markdown(f"**{v['word']}**: {v['meaning']}  \n*Example: {v['example']}*")
                with tab3:
                    st.write(f"**案例分析:** {art.get('case_study')}")
                    for rf in art.get('reflection_flow', []): st.warning(rf)
                
                if st.button("🎙️ 针对此文开启对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.chat_history = []

    with col_right:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            active_art = st.session_state.active_art
            st.info(f"正在深度研读：{active_art['title']}")
            
            # 聊天窗口
            container = st.container(height=500)
            if "chat_history" not in st.session_state: st.session_state.chat_history = []
            
            for m in st.session_state.chat_history:
                with container.chat_message(m["role"]): st.markdown(m["content"])
            
            if prompt := st.chat_input("向教练提问..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with container.chat_message("user"): st.markdown(prompt)
                
                with container.chat_message("assistant"):
                    response = call_coach(prompt, active_art)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            st.info("请在左侧点击【开启对话】按钮启动私教 Session。")
