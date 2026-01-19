import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- 高端明亮 UI 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .welcome-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 8px solid #2563EB; }
    .coach-bubble { background: #EEF2FF; padding: 15px; border-radius: 15px; border: 1px solid #C7D2FE; margin-bottom: 10px; }
    h1, h2, h3 { color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

# 数据加载
def load_data():
    if not os.path.exists("data.json"): return {"items": [], "books": []}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        if "items" not in d: d["items"] = []
        if "books" not in d: d["books"] = []
        return d

data = load_data()

# --- AI Coach 核心引擎 ---
def call_ai_coach(user_input, context_content=""):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key: return "❌ 教练处于离线状态，请检查 API Key 配置。"
    
    # 注入教练人格：专业、尖锐、具有全球视野
    system_prompt = f"""You are the 'Read & Rise' AI Executive Coach. 
    Your goal is to help leaders think deeper. 
    Current Article Context: {context_content}
    Always respond in Chinese, but keep key business terms in English. 
    Encourage the user to apply mental models to their real business cases."""
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7
            })
        return res.json()['choices'][0]['message']['content']
    except:
        return "⚠️ Coach 正在思考中（连接超时），请稍后再试。"

# --- 侧边栏导航 ---
st.sidebar.markdown("<h1 style='color:white; text-align:center;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("模块导航", ["🏠 首页 Dashboard", "🚀 全球商业内参", "📚 资产智库", "🧠 咨询教练 Coach"])

if menu == "🏠 首页 Dashboard":
    st.markdown('<div class="welcome-card"><h1>Hi, Leaders! 👋</h1><p>我是您的 AI Coach。今天已为您更新 10+ 全球信源及 5 本必读名著。您可以随时向我提问。</p></div>', unsafe_allow_html=True)
    
    # 今日推荐
    st.write("")
    if data['items']:
        top = data['items'][0]
        st.subheader(f"🔥 今日首推：{top.get('cn_title')}")
        if os.path.exists(top.get('audio_file', '')):
            st.audio(top['audio_file'])
        
        # 快捷对话入口
        if st.button("🎙️ 就此主题咨询 AI 教练"):
            st.session_state.coach_context = top.get('en_summary')
            st.info("已切换至当前主题，请前往『咨询教练』模块开始对话。")

elif menu == "🚀 全球商业内参":
    st.header("Intelligence Hub")
    for i, item in enumerate(data.get("items", [])):
        with st.expander(f"📍 [{item.get('type')}] {item.get('cn_title')}"):
            if os.path.exists(item.get("audio_file", "")):
                st.audio(item["audio_file"])
            
            # 分页展示
            tabs = st.tabs(["💡 解析", "🔤 词汇", "❓ 反思", "📥 存入智库"])
            with tabs[0]:
                st.write(f"**EN Summary:** {item.get('en_summary')}")
                st.success(f"**CN Analysis:** {item.get('cn_analysis')}")
            with tabs[1]:
                for v in item.get('vocab_cards', []):
                    st.write(f"**{v['word']}** : {v['meaning']}")
            with tabs[2]:
                st.write(item.get('reflection_flow'))
            with tabs[3]:
                if st.button("📥 永久收藏至智库资产", key=f"save_{i}"):
                    data["books"].append({"title": item['en_title'], "insight": item['cn_analysis']})
                    # 此处省略保存 data.json 代码

elif menu == "🧠 咨询教练 Coach":
    st.header("🏹 Read & Rise AI Coach")
    st.caption("基于全球视野与管理思维的 1-on-1 咨询")

    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示历史消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 对话输入
    if prompt := st.chat_input("您可以问我：'这篇文章对我的团队管理有什么启发？'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # 获取上下文（如果用户是从某篇文章点过来的）
            context = st.session_state.get("coach_context", "General business advice")
            response = call_ai_coach(prompt, context)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

elif menu == "📚 资产智库":
    st.header("📚 数字化资产库")
    for b in data.get("books", []):
        st.info(f"**{b['title']}**\n\n{b.get('insight')}")
