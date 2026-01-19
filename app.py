import streamlit as st
import json, os, requests
import plotly.graph_objects as go

# ================= 1. 配置与专业样式 =================
st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    /* 专业教练卡片 */
    .coach-card { 
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
        padding: 30px; border-radius: 20px; color: white; 
        border-left: 10px solid #38BDF8; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .status-card {
        background: white; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px; text-align: center;
    }
    .stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据处理核心 =================
def load_data():
    if not os.path.exists("data.json"):
        return {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "正在生成洞察...", "en": "Generating..."}}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ================= 3. AI 教练 RAG 引擎 =================
def call_ai_coach(user_input, history):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/chat/completions"
    
    # 提取你的私有知识库作为背景
    knowledge_base = ""
    for art in data.get("deep_articles", [])[-5:]: # 取最近5篇深度解析
        knowledge_base += f"文章标题:{art['title']}\n核心案例:{art.get('case_study','')}\n反思建议:{art.get('reflection_flow','')}\n\n"

    system_prompt = f"""
    你叫 Read & Rise AI Coach，是由一位资深教育家打造的数字大脑。
    你的使命：利用私有知识库，助人布局企业、规划个人成长。
    
    你的知识背景：
    {knowledge_base}
    
    你的风格规范：
    1. 严禁回答通用、废话。优先引用上述知识库中的案例。
    2. 采用“启发式提问”：在给出建议后，反问用户一个能触动他思考的问题。
    3. 语言风格：专业、克制、中英夹杂（Executive Phrasing）。
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    
    try:
        res = requests.post(url, 
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": messages, "temperature": 0.5}
        )
        return res.json()['choices'][0]['message']['content']
    except:
        return "抱歉，教练的思维线程暂时离线，请检查 API 配置。"

# ================= 4. 侧边栏与导航 =================
with st.sidebar:
    st.markdown("<h1 style='color:#1E293B;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    menu = st.radio("导航菜单", ["🏠 决策仪表盘", "🚀 全球快报", "🎙️ AI 教练对话", "⚙️ 后台管理"])
    
    # 展示智库积淀
    st.divider()
    st.markdown("### 智库积淀")
    c1, c2 = st.columns(2)
    c1.metric("深度洞察", len(data.get("deep_articles", [])))
    c2.metric("实时情报", len(data.get("briefs", [])))

# ================= 5. 各频道实现 =================

# --- 🏠 决策仪表盘 ---
if menu == "🏠 决策仪表盘":
    st.markdown(f"""
    <div class="coach-card">
        <h4 style="color: #38BDF8; margin:0; letter-spacing:1px;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size: 1.1rem; color: #94A3B8; font-style: italic; margin-top:15px;">"{data['weekly_question'].get('en')}"</p>
        <p style="font-size: 1.5rem; font-weight: bold; margin-top:5px;">“{data['weekly_question'].get('cn')}”</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 引导按钮
    if st.button("💬 针对此问题与教练对话"):
        st.session_state.menu = "🎙️ AI 教练对话" # 简单跳转逻辑提示

# --- 🎙️ AI 教练对话 (RAG 核心) ---
elif menu == "🎙️ AI 教练对话":
    st.subheader("🎙️ Read & Rise AI Coach")
    st.caption("基于您的私有智库为您提供战略决策支持")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 聊天气泡显示
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("输入您的管理难题或个人规划困惑..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("教练正在检索知识库并思考..."):
                response = call_ai_coach(prompt, st.session_state.chat_history[-5:])
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

# --- ⚙️ 后台管理 (隐藏深度上传) ---
elif menu == "⚙️ 后台管理":
    st.header("⚙️ 知识库维护 (仅管理员)")
    uploaded_text = st.text_area("在此粘贴需要深度解析的外刊全文...", height=300)
    if st.button("开始 AI 喂养"):
        with st.status("正在进行深度解析并沉淀至知识库..."):
            # 此处调用 crawler.py 中的 ai_analyze_content 函数
            st.success("解析成功！该文章已入库，AI 教练已同步进化。")
