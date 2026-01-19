import streamlit as st
import json, os, requests

# ================= 1. 初始化 =================
st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

def load_data():
    if not os.path.exists("data.json"): return {"briefs": []}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ================= 2. AI Coach 核心逻辑 =================
def call_coach_with_context(user_input, article_data):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    # 核心：将文章的所有深度解析作为上下文喂给 AI
    context = f"""
    你正在协助用户研读文章：《{article_data['title']}》
    案例分析：{article_data.get('case_study', '')}
    反思流：{article_data.get('reflection_flow', [])}
    管理词汇：{article_data.get('vocab_bank', [])}
    请基于以上内容，以专业教练身份回答。
    """
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_input}
    ]
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
                            headers={"Authorization": f"Bearer {api_key}"},
                            json={"model": "deepseek-chat", "messages": messages})
        return res.json()['choices'][0]['message']['content']
    except: return "Coach 正在思考，请稍后再试。"

# ================= 3. 页面频道渲染 =================
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "🚀 全球快报"])

if menu == "🚀 全球快报":
    # 使用 session_state 记录当前正在对话的文章索引
    if "active_article_index" not in st.session_state:
        st.session_state.active_article_index = None

    col_list, col_chat = st.columns([0.6, 0.4]) # 左侧 60% 列表，右侧 40% 对话

    with col_list:
        st.header("🚀 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.container(border=True):
                st.subheader(f"{art['title']}")
                st.caption(f"源自: {art.get('source')} | 模型: {art.get('related_model')}")
                
                # 中英文摘要展示
                t1, t2, t3 = st.tabs(["摘要", "词汇库", "案例 & 反思"])
                with t1:
                    st.write("**EN:** " + art.get('en_summary', ''))
                    st.write("**中:** " + art.get('cn_summary', ''))
                with t2:
                    for v in art.get('vocab_bank', []):
                        st.write(f"🔹 **{v['word']}**: {v['meaning']}")
                        st.caption(f"Example: {v['example']}")
                with t3:
                    st.write("**案例:** " + art.get('case_study', ''))
                    st.write("**反思提问:**")
                    for q in art.get('reflection_flow', []): st.warning(q)
                
                if st.button("🎙️ 在此开启教练对话", key=f"btn_{i}"):
                    st.session_state.active_article_index = i

    # --- 右侧对话框部分 ---
    with col_chat:
        st.header("🎙️ AI Coach Session")
        if st.session_state.active_article_index is not None:
            active_art = data["briefs"][st.session_state.active_article_index]
            st.info(f"正在对话：《{active_art['title']}》")
            
            # 聊天历史展示
            chat_key = f"history_{st.session_state.active_article_index}"
            if chat_key not in st.session_state: st.session_state[chat_key] = []
            
            for msg in st.session_state[chat_key]:
                with st.chat_message(msg["role"]): st.write(msg["content"])
            
            if user_p := st.chat_input("针对此文向教练提问..."):
                st.session_state[chat_key].append({"role": "user", "content": user_p})
                with st.chat_message("user"): st.write(user_p)
                
                with st.chat_message("assistant"):
                    response = call_coach_with_context(user_p, active_art)
                    st.write(response)
                    st.session_state[chat_key].append({"role": "assistant", "content": response})
        else:
            st.info("请在左侧点击【开启教练对话】开始。")
