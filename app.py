import streamlit as st
import json, os, requests
import plotly.graph_objects as go

# --- 初始化数据 ---
def load_data():
    if not os.path.exists("data.json"):
        return {"briefs": [], "deep_articles": [], "weekly_q_cn": "", "weekly_q_en": ""}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# --- 侧边栏 ---
st.sidebar.title("🏹 Read & Rise")
menu = st.sidebar.radio("频道导航", ["🏠 教练仪表盘", "🚀 爬虫快报", "✍️ 深度精读上传", "🎙️ AI 教练对话"])

# --- 功能 1：主页看板 (中英双语提问) ---
if menu == "🏠 教练仪表盘":
    st.markdown(f"""
    <div style="background: #0F172A; padding: 30px; border-radius: 20px; color: white; border-left: 10px solid #38BDF8; margin-bottom: 25px;">
        <h3 style="color: #38BDF8; margin-top: 0;">🎙️ COACH INQUIRY / 今日教练提问</h3>
        <p style="font-size: 1.1rem; color: #94A3B8; font-style: italic;">“{data.get('weekly_q_en', 'How to leverage AI?')}”</p>
        <p style="font-size: 1.4rem; font-weight: bold;">“{data.get('weekly_q_cn', '你打算如何利用 AI 重新定义核心竞争力？')}”</p>
    </div>
    """, unsafe_allow_html=True)
    # 此处放置雷达图代码...

# --- 功能 2：AI 教练对话 (灵魂功能) ---
elif menu == "🎙️ AI 教练对话":
    st.header("🎙️ Read & Rise AI Coach")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 展示历史消息
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("向教练提问..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # 【关键】将你上传的“深度精读”作为背景知识喂给 AI
            kb_context = str(data["deep_articles"][-3:]) # 取最近3篇深度文章
            
            # 调用 DeepSeek API
            api_key = os.getenv("DEEPSEEK_API_KEY")
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是一位精英商业教练。基于以下智库背景回答：{kb_context}"},
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
            response_text = res.json()['choices'][0]['message']['content']
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- 功能 3：手动上传深度解析 ---
elif menu == "✍️ 深度精读上传":
    st.header("✍️ 投喂 AI 教练深度文章")
    raw_text = st.text_area("粘贴外刊全文...", height=400)
    if st.button("开始深度联动解析"):
        # 调用 crawler 中的深度解析函数并保存到 data.json
        st.success("解析成功！该文章已成为 AI 教练的‘新知识’。")
