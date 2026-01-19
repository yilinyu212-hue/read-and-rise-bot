import streamlit as st
import json, os, requests
import plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise Coach", layout="wide")

# CSS 略（保持之前的专业深蓝风格）

def load_data():
    if not os.path.exists("data.json"):
        return {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "加载中", "en": "Loading"}}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# 侧边栏
menu = st.sidebar.radio("Navigation", ["🏠 教练仪表盘", "🚀 爬虫快报", "✍️ 深度精读上传", "🎙️ 私人教练对话"])

# --- 1. 教练仪表盘 (中英双语提问) ---
if menu == "🏠 教练仪表盘":
    st.markdown(f"""
    <div style="background: #0F172A; padding: 25px; border-radius: 15px; color: white; border-left: 8px solid #38BDF8;">
        <h4 style="color: #38BDF8; margin:0;">🎙️今日教练提问 / DAILY INQUIRY</h4>
        <p style="font-size: 1.1rem; color: #94A3B8; font-style: italic; margin-top:10px;">"{data['weekly_question'].get('en')}"</p>
        <p style="font-size: 1.3rem; font-weight: bold;">“{data['weekly_question'].get('cn')}”</p>
    </div>
    """, unsafe_allow_html=True)
    # 此处放置雷达图展示 deep_articles 的平均分...

# --- 2. 深度精读上传 (解决国内访问问题) ---
elif menu == "✍️ 深度精读上传":
    st.header("✍️ 投喂 AI 教练深度内容")
    content = st.text_area("在此粘贴外刊原文...", height=400)
    if st.button("开始深度解析与联动"):
        with st.spinner("AI 首席教练正在研读并匹配模型..."):
            prompt = f"""深度解析：{content[:3000]}。
            要求返回JSON：{{
                "title": "", "cn_analysis": "", "related_model": "", "related_book": "",
                "scores": {{"战略":80, "视野":90}}, "q_cn": "新的教练提问", "q_en": "New English Question"
            }}"""
            # 调用 AI (此处复用 crawler 中的 ai_call 逻辑)
            res = requests.post(...) # 模拟调用
            new_art = res.json() 
            
            data["deep_articles"].append(new_art)
            data["weekly_question"] = {"cn": new_art['q_cn'], "en": new_art['q_en']}
            save_data(data)
            st.success("深度文章已入库，教练提问已更新！")

# --- 3. 私人教练对话 (基于深度文章库) ---
elif menu == "🎙️ 私人教练对话":
    st.header("🎙️ Read & Rise AI Coach")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("输入你的挑战..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # 【灵魂逻辑】将你上传的所有 deep_articles 标题和关联模型作为上下文
            kb = [f"{a['title']} (模型: {a['related_model']})" for a in data["deep_articles"][-5:]]
            coach_prompt = f"背景知识：{kb}\n用户问题：{prompt}\n请结合背景给出教练式回答。"
            # 调用 AI 并展示...
