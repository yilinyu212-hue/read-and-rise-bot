import streamlit as st
import json, os

# 基础配置
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- UI 视觉：修复侧边栏对比度 & 高级卡片样式 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; font-weight: 500; }
    .stApp { background-color: #F8FAFC; }
    
    /* 档案卡片设计 */
    .hero-card { 
        background: white; padding: 40px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-top: 8px solid #2563EB; 
        text-align: center; margin-bottom: 30px;
    }
    .article-card { 
        background: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #E2E8F0; margin-bottom: 15px;
    }
    .tag { 
        background: #DBEAFE; color: #1E40AF; padding: 4px 12px; 
        border-radius: 6px; font-size: 0.8rem; font-weight: bold; 
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {"items": []}
    return {"items": []}

data = load_data()
items = data.get("items", [])

# --- 侧边栏 ---
st.sidebar.markdown("<h1 style='text-align:center;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align:center; opacity:0.8;'>Educator's Strategic Library</p>", unsafe_allow_html=True)
st.sidebar.divider()
menu = st.sidebar.radio("Navigation", ["🏠 Dashboard", "🚀 Intelligence Hub", "🧠 AI Coach"])

# --- 1. 首页 Dashboard ---
if menu == "🏠 Dashboard":
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.title("Hi, Leaders! 👋")
    if items:
        top = items[0]
        st.markdown(f"### 今日首荐：{top.get('cn_title')}")
        st.write(f"“{top.get('cn_analysis')[:120]}...”")
        if st.button("开始今日学习之旅"):
            st.toast("请点击左侧『Intelligence Hub』查看详细内参")
    else:
        st.info("AI 正在为您扫描全球智库，请稍后...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部数据指标
    col1, col2, col3 = st.columns(3)
    col1.metric("今日更新", len(items))
    col2.metric("涵盖信源", "10 Top Sources")
    col3.metric("AI 状态", "Active")

# --- 2. 深度内参 Intelligence Hub ---
elif menu == "🚀 Intelligence Hub":
    st.header("Intelligence Hub")
    st.caption("同步全球顶级商业与领导力洞察")
    
    if not items:
        st.warning("暂无数据，请检查服务器同步状态。")
    
    for item in items:
        with st.container():
            st.markdown(f"""
            <div class="article-card">
                <span class="tag">GLOBAL BRIEFING</span>
                <h3 style="margin-top:10px;">{item.get('cn_title', 'Loading...')}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("展开研读 (音频 + 案例 + 反思流)"):
                # 音频播放
                if os.path.exists(item.get('audio_file', '')):
                    st.audio(item['audio_file'])
                
                # Tab 分页显示核心内容
                tab1, tab2, tab3 = st.tabs(["💡 深度解析", "📖 行业案例", "🧠 反思流"])
                
                with tab1:
                    st.success(f"**核心视点：**\n{item.get('cn_analysis')}")
                    st.caption(f"英文原题: {item.get('en_title')}")
                
                with tab2:
                    st.write("**针对教育管理者的应用案例：**")
                    st.info(item.get('case_study', '正在根据文章生成匹配案例...'))
                
                with tab3:
                    st.warning(f"**推荐思维模型：** {item.get('mental_model', '第一性原理')}")
                    st.write("**管理者深度反思：**")
                    for q in item.get('reflection_flow', ["如何将此策略应用到您的团队？"]):
                        st.write(f"❓ {q}")

# --- 3. AI 教练 AI Coach ---
elif menu == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    st.info("我是您的 AI 教练，您可以针对上述文章或任何管理难题向我提问。")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
        
    if p := st.chat_input("向教练提问..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            st.markdown("正在结合今日内参为您提供咨询...")
