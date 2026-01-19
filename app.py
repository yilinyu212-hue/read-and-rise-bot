import streamlit as st
import json, os, requests

# 设置页面
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- UI 视觉：修复侧边栏对比度 + 标签化标题 ---
st.markdown("""
<style>
    /* 侧边栏背景与文字颜色修复 */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important; 
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #F8FAFC !important;
        font-weight: 600;
    }
    /* 标签化标题样式 */
    .section-tag {
        background: #2563EB;
        color: white;
        padding: 5px 15px;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
    }
    .stApp { background-color: #F8FAFC; }
    .welcome-card { 
        background: white; 
        padding: 30px; 
        border-radius: 20px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); 
        border-top: 8px solid #2563EB; 
    }
    .vocab-card { background: #F1F5F9; padding: 12px; border-radius: 10px; border-left: 4px solid #3B82F6; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"items": []}
    with open("data.json", "r", encoding="utf-8") as f:
        try:
            d = json.load(f)
            return d if "items" in d else {"items": []}
        except: return {"items": []}

data = load_data()

# --- 侧边栏导航 ---
st.sidebar.markdown("<h1 style='color:white; text-align:center;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
st.sidebar.divider()
menu = st.sidebar.radio("CHANNELS", ["🏠 决策看板 Dashboard", "🚀 全球内参 Intelligence", "🧠 咨询教练 AI Coach"])

if menu == "🏠 决策看板 Dashboard":
    st.markdown('<div class="section-tag">WELCOME</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-card"><h1>Hi, Leaders! 👋</h1><p>专注教育者视野。今日已为您扫描 10+ 全球信源及 5 本管理名著。</p></div>', unsafe_allow_html=True)
    
    if data["items"]:
        st.write("")
        st.markdown('<div class="section-tag">TOP RECOMMENDATION</div>', unsafe_allow_html=True)
        top = data["items"][0]
        with st.container(border=True):
            st.subheader(f"🔥 {top.get('cn_title')}")
            st.caption(f"Original: {top.get('en_title')}")
            # 独立播报
            if os.path.exists(top.get('audio_file', '')):
                st.audio(top['audio_file'])
            st.write(top.get('cn_analysis'))
    else:
        st.info("🕒 资产正在同步中... 请在终端执行 git pull 并确保 crawler.py 已运行。")

elif menu == "🚀 全球内参 Intelligence":
    st.markdown('<div class="section-tag">GLOBAL SOURCES & BOOKS</div>', unsafe_allow_html=True)
    
    if not data["items"]:
        st.warning("暂无内容，请检查 data.json 是否包含数据。")
    
    for i, item in enumerate(data.get("items", [])):
        with st.expander(f"📍 [{item.get('type')}] {item.get('cn_title')}"):
            if os.path.exists(item.get('audio_file','')):
                st.audio(item['audio_file'])
            
            t1, t2, t3, t4 = st.tabs(["💡 深度解析", "📖 案例分析", "🔤 词汇卡", "🧠 反思"])
            with t1:
                st.info(f"**EN Summary:**\n{item.get('en_summary')}")
                st.success(f"**CN Analysis:**\n{item.get('cn_analysis')}")
            with t2:
                st.write(item.get('case_study', '案例整理中...'))
            with t3:
                for v in item.get('vocab_cards', []):
                    st.markdown(f'<div class="vocab-card"><strong>{v["word"]}</strong>: {v["meaning"]}</div>', unsafe_allow_html=True)
            with t4:
                st.write(f"**思维模型:** {item.get('mental_model')}")
                for q in item.get('reflection_flow', []):
                    st.warning(f"❓ {q}")

elif menu == "🧠 咨询教练 AI Coach":
    st.markdown('<div class="section-tag">AI EXECUTIVE COACH</div>', unsafe_allow_html=True)
    # 此处保持之前的 Chat 逻辑...
