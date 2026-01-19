import streamlit as st
import json, os, requests
from datetime import datetime

st.set_page_config(page_title="Read & Rise | Executive Terminal", layout="wide", page_icon="🏹")

# --- 数据管理 ---
def load_data():
    if not os.path.exists("data.json"):
        return {"briefs": [], "books": [], "update_time": ""}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        if "books" not in d: d["books"] = []
        return d

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- AI Coach 逻辑 ---
def call_coach(user_input, art):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key: return "❌ Coach 离线：请在服务器配置 API Key。"
    
    # 资产库上下文
    context = "\n".join([f"资产:{b['title']}\n逻辑:{b['insight']}" for b in data['books']])
    
    prompt = f"你是 Read&Rise 教练。背景文章：{art['title']}。已知资产库逻辑：{context}。请结合这些资产回答：{user_input}"
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
        return res.json()['choices'][0]['message']['content']
    except: return "⚠️ Coach 正在闭关思考，请稍候。"

# --- UI 渲染 ---
st.sidebar.title("🏹 READ & RISE")
menu = st.sidebar.radio("功能模块", ["🏠 Dashboard", "🚀 全球快报", "📚 资产智库", "⚙️ 资产录入"])

if menu == "🏠 Dashboard":
    st.markdown("### Hi, Leaders! 👋")
    st.write(f"今日同步时间：{data.get('update_time', '暂未更新')}")
    
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
        st.caption("🎙️ BBC 风格每日内参 (英音)")
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("今日快报", len(data.get("briefs", [])))
    c2.metric("累计资产", len(data.get("books", [])))

elif menu == "🚀 全球快报":
    for i, art in enumerate(data.get("briefs", [])):
        with st.expander(f"📍 {art['source']} | {art['title']}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🇬🇧 Executive Summary")
                st.write(art.get('en_summary'))
            with col2:
                st.subheader("🇨🇳 深度价值拆解")
                st.write(art.get('cn_analysis'))
            
            # 一键转存智库
            if st.button("📥 存入资产智库", key=f"save_{i}"):
                new_asset = {"title": art['title'], "concept": art['source'], "insight": art['cn_analysis']}
                data["books"].append(new_asset)
                save_data(data)
                st.success("已转存至底层智库！")
            
            # 开启对话
            if st.button("🎙️ 呼叫 Coach", key=f"coach_{i}"):
                st.session_state.active_art = art

    if "active_art" in st.session_state:
        st.divider()
        st.chat_message("assistant").write(f"正在为您解析《{st.session_state.active_art['title']}》，您可以提问。")
        if p := st.chat_input("输入您的问题..."):
            st.chat_message("user").write(p)
            st.chat_message("assistant").write(call_coach(p, st.session_state.active_art))

elif menu == "📚 资产智库":
    st.header("📚 Read & Rise 数字资产库")
    for b in data.get("books", []):
        with st.container(border=True):
            st.subheader(b['title'])
            st.write(b['insight'])

elif menu == "⚙️ 资产录入":
    with st.form("manual_add"):
        t = st.text_input("书名/思维模型")
        i = st.text_area("核心逻辑/洞察")
        if st.form_submit_button("入库"):
            data["books"].append({"title":t, "concept":"Manual", "insight":i})
            save_data(data)
            st.success("资产已入库")
