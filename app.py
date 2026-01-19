import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise | Executive Brain", layout="wide", page_icon="🏹")

# --- UI 视觉：横向导航 + 商务深蓝风格 ---
st.markdown("""
<style>
    /* 隐藏默认侧边栏 */
    [data-testid="stSidebar"] { display: none; }
    
    /* 页面背景 */
    .stApp { background-color: #FBFBFE; }
    
    /* 顶部横向导航样式 */
    .nav-bar {
        display: flex; justify-content: center; gap: 50px;
        background: #0F172A; padding: 15px; border-radius: 0 0 20px 20px;
        margin-bottom: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .nav-item { color: white !important; font-weight: 600; text-decoration: none; cursor: pointer; }
    
    /* 决策看板样式 */
    .hero-card {
        background: white; padding: 40px; border-radius: 20px;
        border-top: 10px solid #2563EB; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .case-box { background: #F1F5F9; padding: 20px; border-radius: 12px; border-left: 5px solid #2563EB; }
</style>
""", unsafe_allow_html=True)

# --- 逻辑处理：导航 ---
if "menu" not in st.session_state: st.session_state.menu = "🏠 决策看板"

# 模拟横向导航栏
st.markdown(f"""
<div class="nav-bar">
    <div style="color:#3B82F6; font-weight:bold; font-size:1.2rem; margin-right:50px;">🏹 Read & Rise</div>
</div>
""", unsafe_allow_html=True)

# 使用 Streamlit columns 模拟按钮点击效果实现导航
col_n1, col_n2, col_n3 = st.columns([1,1,1])
if col_n1.button("🏠 决策看板", use_container_width=True): st.session_state.menu = "🏠 决策看板"
if col_n2.button("🚀 全球内参", use_container_width=True): st.session_state.menu = "🚀 全球内参"
if col_n3.button("🧠 AI 教练", use_container_width=True): st.session_state.menu = "🧠 AI 教练"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {"items": []}
    return {"items": []}

data = load_data()
items = data.get("items", [])

# --- 1. 首页：决策看板 (针对中高层设计) ---
if st.session_state.menu == "🏠 决策看板":
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.title("Hi, Leaders! 👋")
    st.write("今日全球商业视点已为您提炼。")
    
    if items:
        top = items[0]
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader(f"🔥 核心决策建议：{top.get('cn_title')}")
            st.markdown(f"**趋势分析：** {top.get('cn_analysis')[:200]}...")
        with c2:
            st.markdown("### 🧠 今日反思")
            ref = top.get('reflection_flow', ["如何通过此趋势优化您的团队？"])
            st.warning(ref[0] if isinstance(ref, list) else ref)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 快捷入口
    st.markdown("---")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("今日必读", f"{len(items)} 篇")
    sc2.metric("覆盖信源", "10 个")
    sc3.metric("AI 教练", "就绪")

# --- 2. 全球内参：带 AI Coach 联动逻辑 ---
elif st.session_state.menu == "🚀 全球内参":
    st.header("Intelligence Hub")
    for item in items:
        with st.container():
            st.subheader(f"📍 {item.get('cn_title')}")
            
            # 标签页展示
            t1, t2, t3 = st.tabs(["💡 深度解析", "📖 行业案例", "🧠 追问 AI Coach"])
            
            with t1:
                if os.path.exists(item.get('audio_file','')): st.audio(item['audio_file'])
                st.success(item.get('cn_analysis'))
            
            with t2:
                st.markdown('<div class="case-box">', unsafe_allow_html=True)
                st.write(item.get('case_study', '正在加载深度案例...'))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with t3:
                st.write("**针对这篇文章，您可以直接向 AI 教练提问：**")
                # 为每篇文章生成一个独特的对话入口
                user_q = st.text_input(f"针对《{item.get('cn_title')[:10]}》提问：", key=item.get('cn_title'))
                if user_q:
                    st.session_state.menu = "🧠 AI 教练"
                    st.session_state.pending_q = f"基于文章《{item.get('cn_title')}》，我的困惑是：{user_q}"
                    st.rerun()

# --- 3. AI 教练：真正的咨询对话框 ---
elif st.session_state.menu == "🧠 AI 教练":
    st.header("🧠 AI Executive Coach")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 渲染历史对话
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 接收来自内参页面的自动跳转问题
    init_val = st.session_state.get("pending_q", "")
    
    if prompt := st.chat_input("输入您的管理难题..."):
        # 如果有待处理问题，先拼接
        full_prompt = f"{init_val}\n{prompt}" if init_val else prompt
        st.session_state.messages.append({"role": "user", "content": full_prompt})
        with st.chat_message("user"): st.markdown(full_prompt)
        
        # 模拟 AI 回复
        with st.chat_message("assistant"):
            response = f"作为您的 AI 教练，针对您提出的“{prompt}”，我建议从{items[0].get('mental_model', '第一性原理')}出发..."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 清除待处理问题
        if "pending_q" in st.session_state: del st.session_state.pending_q
