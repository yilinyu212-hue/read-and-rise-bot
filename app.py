import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- UI 视觉优化 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .welcome-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-left: 10px solid #2563EB; }
    .vocab-card { background: #EEF2FF; padding: 12px; border-radius: 10px; border-left: 4px solid #4F46E5; margin: 8px 0; }
    h1, h2, h3 { color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"items": []}
    with open("data.json", "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {"items": []}

data = load_data()

# --- AI 教练函数 ---
def ask_coach(query, context=""):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key: return "Coach 正在休假中，请配置 API Key。"
    try:
        res = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"You are a professional Executive Coach. Context: {context}. Respond in Chinese."},
                    {"role": "user", "content": query}
                ]
            })
        return res.json()['choices'][0]['message']['content']
    except: return "Coach 信号不佳，请重试。"

# --- 侧边导航 ---
st.sidebar.title("🏹 Read & Rise")
menu = st.sidebar.radio("Navigation", ["🏠 Dashboard", "🚀 Intelligence Hub", "🧠 AI Coach"])

if menu == "🏠 Dashboard":
    st.markdown('<div class="welcome-card"><h1>Hi, Leaders! 👋</h1><p>2026年1月19日。10个顶级外刊与5本管理名著已为您同步。</p></div>', unsafe_allow_html=True)
    st.divider()
    if data['items']:
        top = data['items'][0]
        st.subheader(f"🔥 今日首荐：{top.get('cn_title')}")
        if os.path.exists(top.get('audio_file','')):
            st.audio(top['audio_file'])
        st.write(top.get('cn_analysis'))

elif menu == "🚀 Intelligence Hub":
    for i, item in enumerate(data.get("items", [])):
        with st.expander(f"📍 [{item.get('type')}] {item.get('cn_title')}"):
            if os.path.exists(item.get("audio_file","")):
                st.audio(item["audio_file"])
            
            t1, t2, t3, t4 = st.tabs(["💡 深度解析", "📖 案例分析", "🔤 词汇卡", "🧠 反思流"])
            with t1:
                st.info(f"**English Summary:**\n{item.get('en_summary')}")
                st.success(f"**中文解析:**\n{item.get('cn_analysis')}")
            with t2:
                st.write(item.get('case_study'))
            with t3:
                for v in item.get('vocab_cards', []):
                    st.markdown(f'<div class="vocab-card"><strong>{v["word"]}</strong>: {v["meaning"]}<br><small>{v["example"]}</small></div>', unsafe_allow_html=True)
            with t4:
                st.write(f"**关联思维模型:** {item.get('mental_model')}")
                for q in item.get('reflection_flow', []):
                    st.warning(f"❓ {q}")

elif menu == "🧠 AI Coach":
    st.header("🏹 Executive Coach")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if p := st.chat_input("向教练提问..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            resp = ask_coach(p)
            st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
