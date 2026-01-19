import streamlit as st
import pandas as pd
import json, os, plotly.graph_objects as go

# 页面配置
st.set_page_config(page_title="Read & Rise Coach", layout="wide")

# 加载数据逻辑
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"articles": [], "books": [], "weekly_question_cn": "", "weekly_question_en": ""}

data = load_data()

# --- 侧边栏 ---
with st.sidebar:
    st.title("🏹 Read & Rise")
    menu = st.radio("导航", ["🏠 教练仪表盘", "✍️ 上传新外刊", "🎙️ AI 教练对话", "📚 智库仓库"])

# --- 首页：教练仪表盘 ---
if menu == "🏠 教练仪表盘":
    st.markdown(f"""
    <div style="background: #0F172A; padding: 25px; border-radius: 15px; color: white; border-left: 8px solid #38BDF8;">
        <h4 style="color: #38BDF8; margin:0;">🎙️今日教练提问 / DAILY INQUIRY</h4>
        <p style="font-size: 1.1rem; color: #94A3B8; font-style: italic; margin-top:10px;">"{data.get('weekly_question_en')}"</p>
        <p style="font-size: 1.3rem; font-weight: bold;">“{data.get('weekly_question_cn')}”</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 此处放置雷达图逻辑... (见前次代码)

# --- 功能一：手动上传并解析 (解决国内访问问题) ---
elif menu == "✍️ 上传新外刊":
    st.header("✍️ 上传外刊文章进行 AI 解析")
    uploaded_text = st.text_area("在此粘贴外刊原文内容...", height=300)
    
    if st.button("开始 AI 深度解析"):
        if uploaded_text:
            with st.status("AI 教练正在研读并匹配模型..."):
                # 这里调用你的 AI 解析函数 (逻辑同前 crawler)
                # 解析完成后，将结果 append 到 data.json 并保存
                st.success("解析完成！已存入智库。")
        else:
            st.warning("请先输入内容")

# --- 功能二：生成你的 AI 教练 (灵魂所在) ---
elif menu == "🎙️ AI 教练对话":
    st.header("🎙️ Read & Rise AI Coach")
    st.markdown("> **我是你的 AI 商业教练。我会基于本站的思维模型和外刊内容回答你的管理困惑。**")

    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("输入你的管理挑战..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # 将最新的几篇文章作为“教练知识背景”
            context = str(data["articles"][-2:]) 
            full_prompt = f"你是一位资深商业教练。背景知识：{context}\n用户问题：{prompt}\n请给出启发式回答："
            
            # 模拟 AI 响应
            # response = your_ai_call(full_prompt) 
            response = "这是一个深刻的问题。结合本周我们分析的《麦肯锡》报告，建议你从'第一性原理'出发..."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
