import streamlit as st
from backend.engine import run_rize_insight
import json, os

# --- 1. 页面配置 ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- 2. 样式注入：打造“内参”质感 ---
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .stExpander { border: none !important; box-shadow: none !important; }
    .insight-card { background: white; padding: 25px; border-radius: 15px; border-left: 5px solid #2563EB; margin-bottom: 20px; }
    .section-header { color: #1E293B; font-weight: 800; font-size: 20px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-top: 30px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏：历史知识库 ---
with st.sidebar:
    st.title("🏹 Read & Rise")
    st.caption("Your daily strategic mentor")
    st.divider()
    
    if os.path.exists("data/knowledge.json"):
        with open("data/knowledge.json", "r") as f:
            history = json.load(f)
            st.subheader("【历史知识库】")
            for item in history[:5]: # 展示最近5篇
                st.button(f"📅 {item['date']} | {item['title'][:10]}...", key=item['date'])

# --- 4. 主界面渲染 ---
page = st.radio("切换视图", ["🏠 今日内参", "⚙️ 后台同步"], horizontal=True)

if page == "🏠 今日内参":
    db = []
    if os.path.exists("data/knowledge.json"):
        with open("data/knowledge.json", "r") as f: db = json.load(f)
    
    if db:
        today = db[0]
        # --- 今日洞察 ---
        st.markdown(f"""
        <div class="insight-card">
            <p style="color:#64748B; font-size:12px;">🏹 READ & RISE | 今日洞察</p>
            <h1 style="margin:0;">{today['title']}</h1>
            <p style="color:#2563EB; font-weight:bold; margin-top:10px;">核心思维模型：{today['model']}</p>
        </div>
        """, unsafe_allow_html=True)

        # --- 深度解析 ---
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown('<div class="section-header">【深度解析】</div>', unsafe_allow_html=True)
            st.markdown(today['content'])
            
            # 模拟语音播报位置
            st.markdown('<div class="section-header">🎧 Listen in English</div>', unsafe_allow_html=True)
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # 示例音频

        with col2:
            st.markdown('<div class="section-header">【给管理者的反思】</div>', unsafe_allow_html=True)
            st.info("**问题 1：** 这个趋势对你下季度的规划有何启发？")
            st.info("**问题 2：** 如果在团队中应用该模型，最大的阻力可能来自哪里？")
    else:
        st.warning("欢迎来到 Read & Rise。请前往后台同步今日内容。")

elif page == "⚙️ 后台同步":
    # 保持原有的同步逻辑...
    st.title("⚙️ 自动化同步后台")
    topic = st.text_input("请输入今日研究主题")
    if st.button("🚀 启动全球抓取"):
        # 调用 backend.engine 逻辑并保存
        pass
