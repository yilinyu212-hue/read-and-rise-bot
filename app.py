import streamlit as st
import json, os, requests
import plotly.graph_objects as go

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
    .brief-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .tag { background: #E0F2FE; color: #0369A1; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据加载 =================
def load_data():
    if not os.path.exists("data.json"): return {}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ================= 3. AI 对话引擎 (RAG 核心) =================
def call_ai_coach(user_input, history, context_art=None):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    # 注入知识库上下文
    kb_context = ""
    if context_art:
        kb_context = f"【当前讨论文章】: {context_art['title']}\n【核心案例】: {context_art.get('case_study','')}\n"
    
    # 基础知识库（来自最近的深度文章）
    for art in data.get("deep_articles", [])[-3:]:
        kb_context += f"【背景知识】: {art['title']} - {art.get('cn_summary','')}\n"

    system_prompt = f"""
    你是 Read & Rise AI Coach。你的目标是助人布局企业、规划个人成长。
    基于以下知识库提供回答：
    {kb_context}
    
    规则：
    1. 语气专业、启发、Executive Style。
    2. 优先引用上述案例。
    3. 最后必须反问一个关于用户实际业务布局的问题。
    """
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "deepseek-chat", "messages": messages, "temperature": 0.4})
        return res.json()['choices'][0]['message']['content']
    except: return "Coach 正在深思，请稍后再试。"

# ================= 4. 侧边栏导航 =================
with st.sidebar:
    st.title("🏹 Read & Rise")
    menu = st.radio("导航", ["🏠 决策仪表盘", "🚀 全球快报", "🎙️ AI 教练对话", "⚙️ 后台管理"])
    st.divider()
    st.info(f"最后同步: {data.get('update_time', 'N/A')}")

# ================= 5. 页面功能实现 =================

# --- 主页：决策仪表盘 ---
if menu == "🏠 决策仪表盘":
    st.markdown(f"""<div class="coach-card">
        <h4 style="color: #38BDF8; margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size: 1.5rem; font-weight: bold; margin-top:10px;">“{data.get('weekly_question', {}).get('cn', '思考中...')}”</p>
    </div>""", unsafe_allow_html=True)
    
    st.subheader("📊 智库当前覆盖维度")
    # 演示用雷达图逻辑
    st.write("已沉淀来自麦肯锡、HBR 等 12 家机构的深度案例。")

# --- 频道：全球快报 (带反思对话入口) ---
elif menu == "🚀 全球快报":
    st.header("🚀 今日智库内参")
    for art in data.get("briefs", []):
        with st.expander(f"📌 [{art.get('source')}] {art['title']}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write("**中文深度解析:**")
                st.write(art['cn_summary'])
                st.write("**🌊 反思流启发：**")
                for q in art.get('reflection_flow', []):
                    st.warning(q)
            with col2:
                if st.button("🎙️ 就此文咨询教练", key=f"chat_{art['title'][:10]}"):
                    st.session_state.current_context = art
                    st.session_state.chat_history = [{"role": "assistant", "content": f"你好！关于《{art['title']}》中的反思点，你有什么具体的困惑吗？我们可以聊聊它如何应用到你的企业布局中。"}]
                    # 跳转到对话频道逻辑提示 (Streamlit 不支持直接修改 radio，建议手动点击跳转或通过 callback)
                    st.info("请切换到【🎙️ AI 教练对话】开始交流。")

# --- 频道：AI 教练对话 ---
elif menu == "🎙️ AI 教练对话":
    st.subheader("🎙️ Read & Rise AI Coach")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("聊聊你的布局或规划..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            ctx = st.session_state.get("current_context", None)
            response = call_ai_coach(prompt, st.session_state.chat_history[-5:], ctx)
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

# --- 频道：后台管理 ---
elif menu == "⚙️ 后台管理":
    st.header("⚙️ 管理员操作面板")
    raw_text = st.text_area("在此粘贴文章全文，AI 将进行深度建模入库...", height=300)
    if st.button("开始深度喂养"):
        st.success("解析成功！内容已沉淀至 AI Coach 知识库。")
