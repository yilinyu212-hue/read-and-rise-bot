import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- UI 视觉 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .welcome-card { background: white; padding: 30px; border-radius: 20px; border-left: 8px solid #2563EB; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .vocab-card { background: #EEF2FF; padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 4px solid #4F46E5; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"items": []}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# --- AI 教练引擎 ---
def ask_coach(query):
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key: return "Coach 离线中..."
    try:
        r = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "deepseek-chat", "messages": [{"role": "system", "content": "You are the Read & Rise Executive Coach. Respond in Chinese."}, {"role": "user", "content": query}]})
        return r.json()['choices'][0]['message']['content']
    except: return "Coach 思考超时..."

# --- 导航 ---
menu = st.sidebar.radio("READ & RISE", ["🏠 Dashboard", "🚀 Intelligence Hub", "🧠 AI Coach"])

if menu == "🏠 Dashboard":
    st.markdown('<div class="welcome-card"><h1>Hi, Leaders! 👋</h1><p>今日 10+ 信源与 5 本名著精华已更新。音频同步就绪。</p></div>', unsafe_allow_html=True)
    if data.get("items"):
        top = data["items"][0]
        st.subheader(f"🔥 首推内容：{top.get('cn_title', 'Loading...')}")
        if os.path.exists(top.get('audio_file', '')): st.audio(top['audio_file'])
        st.write(top.get('cn_analysis'))

elif menu == "🚀 Intelligence Hub":
    for i, item in enumerate(data.get("items", [])):
        with st.expander(f"📍 {item.get('cn_title', 'New Content')}"):
            if os.path.exists(item.get('audio_file','')): st.audio(item['audio_file'])
            t1, t2, t3 = st.tabs(["💡 解析", "🔤 词汇卡", "❓ 反思"])
            with t1:
                st.info(item.get('en_summary'))
                st.success(item.get('cn_analysis'))
            with t2:
                for v in item.get('vocab', []):
                    st.markdown(f'<div class="vocab-card"><strong>{v["w"]}</strong>: {v["m"]}</div>', unsafe_allow_html=True)
            with t3:
                st.write(f"**模型:** {item.get('model')}")
                st.write(item.get('reflection'))

elif menu == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if p := st.chat_input("向教练提问..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            res = ask_coach(p)
            st.markdown(res)
            st.session_state.msgs.append({"role": "assistant", "content": res})
